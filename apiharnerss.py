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

URL = f'http://{socket.gethostname()}:8000'

def FormatDate(input):
    rmatch = re.match(r'^Web\s+Only.+?([0-9]{4})',input)
    if rmatch != None:
        return f'{rmatch[1]}-01-01'
    return "{:%Y-%m-%d}".format(datetime.strptime(input,'%d-%b-%y'))

def GetAll(page):
    data = []
    r = Get(f"{page}?page=1")
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
def LoadWine(producerdata):
    notmatch = 0
    grapeinfo = GetVarietal()
    #open review csv fiew 
    df = pd.read_csv("winespectator.csv", encoding="utf-8")
    payload = []
    for house,wines in df.groupby(["house"]):
        houseinfo = next(filter(lambda x : x['slug'] == slugify(house) , producerdata), None)
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
    blendname = GetAll("api/blendvarietal/")

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

    if gtype.values[0] == "red":
        if information.country.values[0].lower() == "france":
            if information.terroir.values[0].lower().__contains__("Côtes du Rhône".lower()) or information.terroir.values[0].lower().__contains__("châteauneuf"):
                return "Red Rhone Blend"
            elif information.region.values[0].lower().__contains__("Northern Rhône".lower()):
                return "Syrah"
            elif information.region.values[0].lower().__contains__("Côte de Beaune".lower()) or \
                 information.region.values[0].lower().__contains__("Côte de Nuits".lower()) or \
                 information.region.values[0].lower().__contains__("Chalonnaise".lower()) or \
                 information.region.values[0].lower().__contains__("Other Burgundy".lower()):
                return "Pinot Noir"
            else:
                return "Unknown-Red-France"
        elif information.country.values[0].lower() == "spain":
            #Ribera del Duero
            if information.terroir.values[0].lower().__contains__("Ribera del Duero"):
                return "Tempranillo"
            else:
                return "Unknow-Red-Spain"
        else:
            return "Unknown-Red-Type"

    elif gtype.values[0] == "white":
         if information.country.values[0].lower() == "france":
            if information.region.values[0].lower().__contains__("chablis") or \
               information.region.values[0].lower().__contains__("Côte de Beaune".lower()) or \
               information.region.values[0].lower().__contains__("Mâcon".lower()) or \
               information.region.values[0].lower().__contains__("Chalonnaise".lower()) or \
               information.region.values[0].lower().__contains__("Côte de Nuits".lower()) or \
               information.region.values[0].lower().__contains__("Other Burgundy".lower()):
                return "Chardonnay"
            else:
                return "Unknown-White-France"
         else:
             return "Unknow-White-Country"
    else:
        return "unknown-White-Type"

    return "unknown"

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

def LoadWSWines():
    unmatched = {}
    #get varieal
    grapes = GetVarietal()
    excel_file = pd.ExcelFile("winestoload.xlsx")
    df_wines = excel_file.parse('wines')
    df_utf8_data = excel_file.parse('original_data')
    for producer, wines in df_wines.groupby(['house']):
        data = [(i,w) for i,w in wines.iterrows()]
        for d in data:
            row = df_utf8_data[df_utf8_data.id == d[1].id]
            response = Get(f"api/producer/{slugify(row.house.values[0])}/")
            info = row.terroir.values[0] + " " + row.observation.values[0] + " " + row.region.values[0]
            g = GetBlendName(info,grapes)
            if len(g) == 0:
                AOCRuleBased(df_wines[df_wines.id == d[1].id].type, row)
                if row.region.values[0] in unmatched:
                    unmatched[row.region.values[0]] = unmatched[row.region.values[0]] + 1
                else:
                    unmatched.update({row.region.values[0] : 1})
            else:
                print(g)
    print(f"Items to work: {unmatched}")

if __name__ == "__main__":
    #Populate Random Cellar
    #resutls = LoadProducers()
    #LoadWine(resutls)
    #LoadCellar()
    #LoadReviews()
    #LoadDataModel()
    LoadWSWines()