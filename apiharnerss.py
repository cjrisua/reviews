import requests, json
from requests.exceptions import HTTPError
from requests.auth import HTTPBasicAuth
import pandas as pd
import re
import itertools
from datetime import datetime
from django.utils.text import slugify
from array import *
from analytics.utils.smartwine import WineFingerPrint
import socket, chardet
from sklearn.feature_extraction.text import CountVectorizer
from progress.bar import IncrementalBar

URL = f'http://{socket.gethostname()}:8000'



def FormatDate(input):
    rmatch = re.match(r'^Web\s+Only.+?([0-9]{4})',input)
    if rmatch != None:
        return f'{rmatch[1]}-01-01'
    return "{:%Y-%m-%d}".format(datetime.strptime(input,'%d-%b-%y'))

def GetAll(page):
    data = []
    r = Get(f"{page}")
    count = r["count"]
    itemsperset = len(r["results"])
    while r["next"] != None:
        data.extend(r["results"])
        r = Get(re.match(URL+"/(.+?$)",r["next"]).groups(0)[0])
    data.extend(r["results"])
    return data

def Get(page):
    try:
        response = requests.get(f"{URL}/{page}")
        response.raise_for_status()
        # access JSOn content
        return response.json()
        
        return 
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

def Post(page, **kargs):
    headers = {'content-type': 'application/json'}
    response = requests.post(f"{URL}/{page}" , auth=HTTPBasicAuth('admin','password123'), data=json.dumps(kargs["payload"]), headers=headers)
    #jsonResponse = response.json()
    #print(jsonResponse)
    return response

def LoadCountries():
    df = pd.read_csv("country_code.csv")
    filter = df[df.WWPR == "Y"]
    data = [{ "name": c.Country, "abbreviation": c.Alpha3, "slug": slugify(c.Country),'productionrank': c.Rank} for r,c in filter.iterrows()]
    for d in data:
        Post("api/country/",payload = d)

#terroirs = GetAll("api/terroir/")
def LoadReviews():
    #read country file
    countrydf = pd.read_csv("country_code.csv")

    #open review csv fiew 
    df = pd.read_csv("winespectator.csv", encoding="utf-8")
    payload = []
    for house,wines in df.groupby(["house"]):
        dataset = {"name": house, "wines":[]}
        for index, row in wines.iterrows():
            wineset = {
                        "name" : row["terroir"], 

                        "country": countrydf[countrydf.Country==row["country"]].Alpha3.head(1).values[0],
                        "region": row["region"],
                        "terroir": "",
                        "vintage":
                            [{"year": row["vintage"], 
                            "price":  "N/A"  "N/A" if re.match(r"\$(\d+)(\.\d+)?",row["releasedprice"]) is None else re.search(r"[0-9\.,]+",row["releasedprice"])[0],
                            "observations" : [{ "critic" : '2',
                                     "observation": row['observation'],
                                     "score" : row['score'],
                                     "issuedate" : FormatDate(row['issuedate']),
                                   },]
                            }],
                    }
            dataset["wines"].append(wineset)
        Post("api/wine/",payload = dataset)

def isvinifera(name,string):

    result = re.search (f'(^|[^a-z]){name}($|[^a-z])',string)
    
    return False if result is None else True
def LoadWine():
    producerdata = []
    notmatch = 0
    grapeinfo = GetVarietal()
    grape_df =  pd.DataFrame(grapeinfo)

    #open review csv fiew 
    df = pd.read_csv("winespectator.csv", encoding="utf-8")
    payload = []
    for house,wines in df.groupby(["house"]):

        houseinfo = next(filter(lambda x : x['slug'] == slugify(house) , producerdata), None)
        if houseinfo is None:
             houseinfo = Get(f'api/producer/{slugify(house)}/')
             producerdata.append(houseinfo)
            
        print(f"Producer {house} [{houseinfo['id']}]")
        for index, wine in wines.iterrows():
            #Find Grape Info...
            slugifywine = slugify(wine.terroir + "-" + wine.observation)
            grapematches = [grape for grape in grapeinfo if isvinifera(grape['slug'],slugifywine)]

            if len(grapematches) == 0:
                if wine.region == "Southern Rhône":
                    print("Red Rhone Blend?")
                elif wine.region == "Champagne":
                    print(wine.region)
                else:
                    print("No Match found")
            else:
                names = set([name['slug'] for name in grapematches])
                if len(names) == 1:
                    print(names)
                    notmatch = notmatch + 1
                else:
                    print(f"Blend of: {names}")
    print(f"{notmatch} not matched")

            
def GetVarietal():
    varietal = GetAll("api/varietal/")
    blendname = GetAll("api/mastervarietal/")

    vinifera_list = [{"id":v['id'], "type":"v" , "slug": v['slug'], "name" : v['name']} for v in varietal]
    vinifera_list.extend( [{"id": b['id'],"type":"b", "slug": slugify(b['name']), "name" : b['name']} for b in blendname])

    return vinifera_list

def LoadProducers():
    #Get database 
    data = []
    r = Get("api/producer/?page=1")
    if r is not None:
        count = r["count"]
        itemsperset = len(r["results"])
        while r["next"] != None:
            data.extend([{"id": p['id'], "slug" : p['slug']} for p in r["results"]])
            r = Get(r["next"][37:])
        data.extend([{"id": p['id'], "slug" : p['slug']} for p in r["results"]])
        print(f"Database Producers: {data}")

     #open review csv fiew 
    df = pd.read_csv("winespectator.csv", encoding="utf-8")
    slugdata = [slug['slug'] for slug in data]
    localproducer_list = [{"name":p, "slug": slugify(p)} for p in df.house.unique() if slugify(p) not in slugdata]
    for p in localproducer_list:
        Post('api/producer/',payload=p )
    
    return data

def LoadCellar():
    traindict = {}
    data = []
    r = Get("api/wine/?page=1")
    count = r["count"]
    itemsperset = len(r["results"])
    while r["next"] != None:
        data.append(r["results"])
        r = Get(r["next"][22:])
    producers = [(producer['id'],producer['name'],producer['wines']) for i in data for producer in i]
    traindict = [{r:None} for r in set([c['region'] for w in producers for c in w[2]])]

    for p in producers:
        for c in p[2]:
            myfilter = list(filter(lambda x : c['region'] in x and x[c['region']] is None , traindict))
            if len(myfilter) > 0:
                index = traindict.index(myfilter[0])
                item = {c['region'] : c['vintage'][0]['id']}
                traindict[index].update(item)
    for trainw in traindict:
        dataset = {
            "collectible": list(trainw.values())[0],
            "storage": 1,
            "cellar": 1,
            "status": "added"
        }
        Post("api/cellar/",payload = dataset)
def LoadDataModel():
   df = pd.read_csv("winespectator_with_type.csv", encoding="utf-8")
   smartwine = WineFingerPrint(df)

def AOCRuleBased(gtype,information):
    rules = {'Spain': 
                {'red':[{'Tempranillo' :['Rioja','Ribera del Duero']}]}
            }
    if gtype.lower() == "red":
        if information.country.values[0].lower() == "france":
            if information.terroir.values[0].lower().__contains__("Côtes du Rhône".lower()) or \
                information.terroir.values[0].lower().__contains__("châteauneuf") or \
                information.region.values[0].lower().__contains__("Southern Rhône".lower()):
                return [("Red Rhone Blend",1)]
            elif information.region.values[0].lower().__contains__("Northern Rhône".lower()):
                return [("Syrah",1)]
            elif information.region.values[0].lower().__contains__("Côte de Beaune".lower()) or \
                 information.region.values[0].lower().__contains__("Côte de Nuits".lower()) or \
                 information.region.values[0].lower().__contains__("Chalonnaise".lower()) or \
                 information.region.values[0].lower().__contains__("Mâcon".lower()) or \
                 information.region.values[0].lower().__contains__("Other Burgundy".lower()):
                return [("Pinot Noir",1)]
            elif information.region.values[0].lower().__contains__("Graves".lower()):
                return [("Left Bordeaux Blend",1)]
            elif information.region.values[0].lower().__contains__("Bordeaux".lower()):
                return [("Red Bordeaux Blend",1)]
            elif re.search(r"champagne",information.terroir.values[0].lower()) is not None:
                return [("Champagne",1)]
        elif information.country.values[0].lower() == "spain":
            #Ribera del Duero
            if information.terroir.values[0].lower().__contains__("Rioja".lower()) or \
               information.terroir.values[0].lower().__contains__("Ribera del Duero".lower()) or \
               information.terroir.values[0].lower().__contains__("Toro".lower()) or \
               information.terroir.values[0].lower().__contains__("Viño de la Tierra de Castilla y León".lower()) or \
               information.terroir.values[0].lower().__contains__("Navarra".lower()) or \
               information.terroir.values[0].lower().__contains__("La Mancha".lower()) or \
               information.terroir.values[0].lower().__contains__("Viño de la Tierra de Castilla".lower()):
               return [('tempranillo',1)]
            elif information.terroir.values[0].lower().__contains__("Ribeira Sacra".lower()) or \
                 information.terroir.values[0].lower().__contains__("Bierzo".lower()):
                return [('mencia',1)]
            elif information.terroir.values[0].lower().__contains__("Priorat".lower()) or \
                 information.terroir.values[0].lower().__contains__("Campo de Borja".lower()):    
                return [('garnacha red blend',1)]
            elif information.terroir.values[0].lower().__contains__("Cariñena".lower()) or \
                 information.terroir.values[0].lower().__contains__("Terra Alta".lower()):
                return [('garnacha',1)]
            elif information.terroir.values[0].lower().__contains__("Montsant".lower()):
                return [('red rhone blend',1)]
            elif information.terroir.values[0].lower().__contains__("Pago de Otazu".lower()) or \
                 information.terroir.values[0].lower().__contains__("Jerez".lower()) or \
                 information.terroir.values[0].lower().__contains__("Penedès".lower()) or \
                 information.terroir.values[0].lower().__contains__("Conca de Barberà".lower()) or \
                 information.terroir.values[0].lower().__contains__("El Hierro".lower()) or \
                 information.terroir.values[0].lower().__contains__("Monterrei ".lower()) or \
                 information.terroir.values[0].lower().__contains__("Jumilla".lower()):
                  return [('red blend',1)]
            elif information.terroir.values[0].lower().__contains__("Tintilla Viño de la Tierra de Cadiz".lower()) or \
                 information.terroir.values[0].lower().__contains__("Andalucía".lower()) or \
                 information.terroir.values[0].lower().__contains__("Tintilla de Rota".lower()):
                 return [('graciano',1)]
        elif information.country.values[0].lower() == "italy":
            if re.search(r"(Barolo|Barbaresco|Valtellina|Gattinara)",information.terroir.values[0].lower(),flags=re.IGNORECASE) is not None:
                return [('nebbiolo',1)]
            elif re.search(r"Etna",information.terroir.values[0].lower(),flags=re.IGNORECASE) is not None:
                return [("nerello mascalese",1)]
            elif re.search(r"Toscana",information.terroir.values[0].lower(),flags=re.IGNORECASE) is not None:
                return [("SuperTuscan Blend",1)]
            elif re.search(r"Taurasi",information.terroir.values[0].lower(),flags=re.IGNORECASE) is not None:
                return [("Aglianico",1)]
            elif re.search(r"Cerasuolo",information.terroir.values[0].lower(),flags=re.IGNORECASE) is not None:
                return [("red blend",1)]
            elif re.search(r"(^|\s)Gavi($|\s)",information.terroir.values[0].lower(),flags=re.IGNORECASE) is not None:
                return [("cortese",1)]
            elif re.search(r"(^|\s)Cirò($|\s)",information.terroir.values[0].lower(),flags=re.IGNORECASE) is not None:
                return [("gaglioppo",1)]
        elif information.country.values[0].lower() == "portugal":
            if re.search(r"((ruby|tawny|vintage)?(^|\s)port($|\s))",information.terroir.values[0].lower()) is not None or\
               re.search(r"Douro",information.terroir.values[0].lower(), flags=re.IGNORECASE) is not None:
               return [('port blend',1)]
        elif information.country.values[0].lower() == "United States":
            if re.search(r"(Napa|Monte Bello)",information.terroir.values[0].lower()) is not None:
                return [('red blend',1)]
    elif gtype.lower() == "white":
         if information.country.values[0].lower() == "france":
            if information.region.values[0].lower().__contains__("Sauternes".lower()) or \
               information.region.values[0].lower().__contains__("Barsac".lower()):
                return [("Sémillon",1), ("Sauvignon Blanc",1)]
            elif re.search(r"champagne",information.terroir.values[0].lower()) is not None:
                return [("Champagne",1)]
            elif information.region.values[0].lower().__contains__("chablis") or \
               information.region.values[0].lower().__contains__("Côte de Beaune".lower()) or \
               information.region.values[0].lower().__contains__("Mâcon".lower()) or \
               information.region.values[0].lower().__contains__("Chalonnaise".lower()) or \
               information.region.values[0].lower().__contains__("Côte de Nuits".lower()) or \
               information.region.values[0].lower().__contains__("Other Burgundy".lower()):
                return [("Chardonnay",1)]
            elif information.region.values[0].lower().__contains__("Alsace".lower()):
                return [("Riesling Blend",1)]
            elif information.terroir.values[0].lower().__contains__("Condrieu".lower()):
                return [("Viognier",1)]
            elif information.region.values[0].lower().__contains__("Graves".lower()) or \
                 information.region.values[0].lower().__contains__("Bordeaux".lower()):
                return [("White Bordeaux Blend",1)]
            elif information.region.values[0].lower().__contains__("Rhône".lower()):
                return [("White Rhone Blend",1)]
         elif information.country.values[0].lower() == "italy":
            if re.search(r"Etna",information.terroir.values[0].lower(),flags=re.IGNORECASE) is not None:
                return [("Carricante",1)]
            elif re.search(r"Greco",information.terroir.values[0].lower(),flags=re.IGNORECASE) is not None:
                return [("greco",1)]
            elif re.search(r"(^|\s)Gavi($|\s)",information.terroir.values[0].lower(),flags=re.IGNORECASE) is not None:
                return [("cortese",1)]
         elif information.country.values[0].lower() == "spain":
             if information.terroir.values[0].lower().__contains__("Manzanilla".lower()) or \
                information.terroir.values[0].lower().__contains__("Jerez".lower()):
                 return [('palomino',1)]
             elif information.terroir.values[0].lower().__contains__("Alella".lower()) or \
                  information.terroir.values[0].lower().__contains__("El Hierro".lower()) or \
                  information.terroir.values[0].lower().__contains__("Monterrei ".lower()) or \
                  information.terroir.values[0].lower().__contains__("Jumilla".lower()):
                  return [('white blend',1)]
             elif information.terroir.values[0].lower().__contains__("Rioja".lower()):
                  return [('macabeo',1)]
             elif information.terroir.values[0].lower().__contains__("Rueda".lower()):
                  return [('verdejo',1)]
             elif information.terroir.values[0].lower().__contains__("Rias Baixas".lower()):
                  return [('albariño',1)]
             elif information.terroir.values[0].lower().__contains__("Brut".lower()) or \
                  information.terroir.values[0].lower().__contains__("Cava".lower()):
                  return [('Macabeo',1),('Xarello',1),('Parellada',1)]
             elif  information.terroir.values[0].lower().__contains__("Terra Alta".lower()):
                  return [('grenache blanc',1)]
             elif information.terroir.values[0].lower().__contains__("Txakolina".lower()) or \
                  information.terroir.values[0].lower().__contains__("Utiel-Requena".lower()):
                  return [('rosé blanc',1)]
             elif information.terroir.values[0].lower().__contains__("Txakolina".lower()) or \
                  information.terroir.values[0].lower().__contains__("Ribeiro".lower()):
                  return [('treixadura',1)]
             elif information.terroir.values[0].lower().__contains__("Xarel".lower()):
                 return [('Xarello',1)]   
             elif information.terroir.values[0].lower().__contains__("Valdeorras".lower()):
                 return [('godello',1)]  
             elif information.terroir.values[0].lower().__contains__("Conca de Barberà".lower()): 
                 return [('chardonnay',1)]  
         elif information.country.values[0].lower() == "portugal":
            if re.search(r"((ruby|tawny|vintage)?(^|\s)port($|\s))",information.terroir.values[0].lower()) is not None or\
               re.search(r"Douro",information.terroir.values[0].lower(), flags=re.IGNORECASE) is not None:
               return [('white blend',1)]

    if re.search(r"(^|\s)brut($|\s)",information.terroir.values[0].lower(),flags=re.IGNORECASE) is not None or\
       re.search(r"(^|\s)Blanc(s)?\sde\s(Blancs|Noirs)($|\s)",information.terroir.values[0].lower(),flags=re.IGNORECASE) is not None:
                return [("Champagne",1)]

    return None

def GetBlendName(info,grapes):
    vocabulary = list(set([str(g['name']).lower() for g in grapes]))
    cv = CountVectorizer(vocabulary=vocabulary, ngram_range=(1, 2))
    #vectorizer.fit_transform(vocabulary)
    #bag_of_words = vectorizer.transform([info])
    bag_of_words = cv.fit_transform([info.lower()])

    sum_words = bag_of_words.sum(axis=0) 
    words_freq = [(word, sum_words[0, idx]) for word, idx in     cv.vocabulary_.items()]
    words_freq =sorted(words_freq, key = lambda x: x[1], reverse=True)
    return [w for w in words_freq if w[1] > 0]

def GetTerroir(winename, country, region):
    country_regions = list(filter(lambda c: c['country_name'] == country, terroirs))
    vocabulary = list(set([str(t['name']).lower() for t in country_regions]))
    cv = CountVectorizer(vocabulary=vocabulary, ngram_range=(1, 4))
    bag_of_words = cv.fit_transform([winename.lower() + " " + region.lower()])
    sum_words = bag_of_words.sum(axis=0) 
    words_freq = [(word, sum_words[0, idx]) for word, idx in     cv.vocabulary_.items()]
    words_freq =sorted(words_freq, key = lambda x: x[1], reverse=True)
    return [w for w in words_freq if w[1] > 0]

    print(len(country_regions))
def addBlend(winetypeid,varietals):

    varietals = [int(i) for i in varietals]
    varietals.sort()
    print("search blend!")
    master_varietal_response = GetAll("api/blendvarietal/?items=" + ','.join(str(v) for v in varietals))
    if len(master_varietal_response) == 0:
        response = Post('api/blendvarietal/',payload={'mastervarietal': winetypeid, 'varietal' :varietals})
        return json.loads(response.content)['id']
    else:
        if len(master_varietal_response) > 0:
            #Try to Exact Match
            #varietals.sort()
            varietal_list = [varietal for varietal in [result['varietal'] for result in master_varietal_response] if len(varietal) == len(varietals)]
            
            for index, blend_varietal in enumerate(varietal_list):
                blend_varietal.sort()
                if blend_varietal == varietals:
                    return master_varietal_response[index]['id']

            response = Post('api/blendvarietal/',payload={'mastervarietal': winetypeid, 'varietal' :varietals})
            return json.loads(response.content)['id']

def LoadWSWines():
    unmatched = {}
    #get varieal
    grapes = GetVarietal()
    grapes_df = pd.DataFrame(grapes)
    excel_file = pd.ExcelFile("winestoload.xlsx")
    df_wines = excel_file.parse('wines')
    #df_wines = df_wines[(df_wines.region == 'Portugal')]
    df_utf8_data = excel_file.parse('original_data')

    bar = IncrementalBar('Loading', max=df_wines.shape[0], suffix='%(percent)d%%')

    for producer, wines in df_wines.groupby(['house']):
        data = [(i,w) for i,w in wines.iterrows()]
        for d in data:
            #bar.next()
            winetype = df_wines[df_wines.id == d[1].id].type.values[0]

            row = df_utf8_data[df_utf8_data.id == d[1].id]
            producer_dict = Get(f"api/producer/{slugify(row.house.values[0])}/")

            if producer_dict is None:
                continue

            info = row.terroir.values[0] + " " + row.observation.values[0] + " " + row.region.values[0]
            g = GetBlendName(info,grapes)
            
            if len(g) == 0:
                g = AOCRuleBased(winetype, row)
                if g is None:
                    if row.region.values[0] in unmatched:
                        unmatched[row.region.values[0]] = unmatched[row.region.values[0]] + 1
                    else:
                        unmatched.update({row.region.values[0] : 1})
                    #print(f"{row.house.values[0]}@{row.terroir.values[0]}@{row.country.values[0]}@{row.region.values[0]}")
            else:
                #print(g)
                pass
            #print(f"{df_wines[df_wines.id == d[1].id].type.values[0]}@{g}")

            varietal_info = None
            
            if g is None:
                varietal_info = grapes_df[grapes_df['slug'] == 'none'].id.values[0]
            else:
                if len(g) > 1:
                    results = grapes_df[(grapes_df['type'] == 'v') & (grapes_df['slug'].isin([slugify(grape[0]) for grape in g]))]
                    if results.shape[0] > 0:
                        varietal_info = [id for id in results.id.values]
                        if winetype.lower() == "red" or winetype.lower() == "white":
                            #Red Blend
                            varietal_info = addBlend(int(grapes_df[grapes_df['slug'] == f'{winetype.lower()}-blend'].id.values[0]), [id for id in results.id.values])
                        else:
                            print(f"Invalid wine type: {winetype}")
                            raise
                    else:
                        varietal_info = grapes_df[grapes_df['slug'] == 'none'].id.values[0]
                else:
                    results = grapes_df[(grapes_df['type'] == 'b') & (grapes_df['slug'].isin([slugify(grape[0]) for grape in g]))]
                    varietal_info = addBlend(int(results.id.values[0]),[grapes_df[grapes_df['slug'] ==slugify(g[0][0])].id.values[0]])
                    #print(f"single varietal")
                    
            #xxxxx
            terroir_name = GetTerroir(row.terroir.values[0], row.country.values[0], row.region.values[0])
            print(terroir_name)
            wine = {
                "producer": producer_dict['id'],
                "varietal": varietal_info,
            }
            #print(wine)
    bar.finish()
    print(f"Items to work: {unmatched}")

if __name__ == "__main__":
    #LoadCountries()
    #Populate Random Cellar
    #resutls = LoadProducers()
    #LoadWine()
    #LoadCellar()
    #LoadReviews()
    LoadDataModel()
    #LoadWSWines()