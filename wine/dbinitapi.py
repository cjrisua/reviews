import requests, json, re
from requests.exceptions import HTTPError
from requests.auth import HTTPBasicAuth
import pandas as pd
import socket
from django.utils.text import slugify
from progress.bar import IncrementalBar
from functools import lru_cache

URL = f'http://{socket.gethostname()}:8000'
country_regions = []
cache_region ={}

def FormatDate(input):
    rmatch = re.match(r'^Web\s+Only.+?([0-9]{4})',input)
    if rmatch != None:
        return f'{rmatch[1]}-01-01'
    return "{:%Y-%m-%d}".format(datetime.strptime(input,'%d-%b-%y'))
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

def Post(page, **kargs):
    headers = {'content-type': 'application/json'}
    return requests.post(f"{URL}/{page}" , auth=HTTPBasicAuth('admin','password123'), data=json.dumps(kargs["payload"]), headers=headers)


def RegionLookup(name):
    global country_regions
    global cache_regions

    #check cache
    if name[0] not in cache_region:
        cache_region.update({name[0]:{}})
    
    from_cache = cache_region[name[0]]

    if name not in from_cache:
        parentid = None
        region_dbinfo = next((item for item in country_regions if slugify(item["name"]) == slugify(name)), None)

        if region_dbinfo is not None:
            parentid = region_dbinfo['id']
            data = {name : parentid}
            cache_region[name[0]].update(data)
        return parentid

    else:
         return from_cache[name]

def ProcessTerroir(terroirs, countryid):
    global country_regions
    parentid = None
    for terroir in enumerate(terroirs):
        if terroir[1] == "Unknown" or terroir[1] == "None":
            continue

        regionid = RegionLookup(terroir[1])

        if regionid is None:

            payload = {"name" : terroir[1], 
            "parentterroir" : parentid,
            "isappellation": False if terroir[0] != 3 else True,
            "isvineyard": False if terroir[0] != 4 else True,
            "country" : countryid
            }
            response = Post("api/terroir/",payload = payload)
            country_regions.append(json.loads(response.content))
            parentid = json.loads(response.content)['id']
        else:
            parentid = regionid
    '''
    if info[1] == "Unknown" or info[1] == "None":
        continue
    region_dbinfo = next((item for item in country_regions if slugify(item["name"]) == slugify(info[1])), None)
    if region_dbinfo is not None:
        parentid = region_dbinfo['id']
    nex(Region())
    '''
    '''
    payload = {"name" : info[1] , 
        "parentterroir" : parentid,
        "isappellation": False if info[0] != 3 else True,
        "isvineyard": False if info[0] != 4 else True,
        "country" : [c for c in countries if c['name']==country][0]['id']
        }
    response = Post("api/terroir/",payload = payload)
    country_regions.append(json.loads(response.content))
    parentid = json.loads(response.content)['id']
    '''

def LoadCountry():
    #Load Country
    countries =(
            ('FRA','France'),
            ('NZL','New Zealand'),
            ('AUS','Australia'),
            ('CHL','Chile'),
            ('ARG','Argentina'),
            ('USA','United States'),
            ('PRT','Portugal'),
            ('ESP','Spain'),
            ('ITA','Italy'),
            ('HUN','Hungary'),
            ('DEU','Germany'),
            ('AUT','Austria'),
            ('CAN', 'Canada'),
            ('ISR','Israel'),
            ('ZAF', 'South Africa'),
            ('CHE','Switzerland'))
    countries = [{"name": name, "abbreviation": abbreviation} for abbreviation, name in countries]
    for country in countries:
        response = Post("api/country/",payload = country)
def LoadRegions():

    global country_regions
    global cache_regions

    countries = [c for c in GetAll("api/country/")]

    df = pd.read_csv("terroir.csv", encoding='utf8')

    for country_key in df.groupby(by='country'):
        country = "United States" if country_key[0] == "USA" else country_key[0]
        country_regions = [r for r in GetAll(f"api/terroir/?country={slugify(country)}")]

        bar = IncrementalBar(f'Loading {country_key[0]} [{len(country_regions)}]', max=country_key[1].shape[0], suffix='%(percent)d%%')
        cache_regions = {}
        for row in country_key[1].sort_values(by=['country','region','subregion']).iterrows():
            bar.next()
            region = row[1].region
            subregion = row[1].subregion
            appellation = row[1].appellation
            vineyard = row[1].vineyard
            data = [country, region, subregion, appellation, vineyard]
            
            if len([empty for empty in data if empty == "Unknown"]) > 2:
                continue
            country_info = next((c for c in countries if c['name'] == country),None)
            ProcessTerroir(data, country_info['id'] )
            
            
        bar.finish()
    '''     
    for row in df.sort_values(by=['country','region','subregion'])[df['country'] == 'France'].iterrows():
        
        #
        country = "United States" if row[1].country == "USA" else row[1].country
        country_regions = [r for r in regions if r['country_name'] == row[1].country]
        
        region = row[1].region
        subregion = row[1].subregion
        appellation = row[1].appellation
        vineyard = row[1].vineyard
        data = [country, region, subregion, appellation, vineyard]

        if len([empty for empty in data if empty == "Unknown"]) > 2:
            continue

        parentid = None
        for info in enumerate(data):
            if info[1] == "Unknown" or info[1] == "None":
                continue
            region_dbinfo = [r for r in country_regions if slugify(r['name']) == slugify(info[1])]
            if len(region_dbinfo) > 0:
                parentid = region_dbinfo[0]['id']
                continue

            payload = {"name" : info[1] , 
                "parentterroir" : parentid,
                "isappellation": False if info[0] != 3 else True,
                "isvineyard": False if info[0] != 4 else True,
                "country" : [c for c in countries if c['name']==country][0]['id']
                }
            response = Post("api/terroir/",payload = payload)
            country_regions.append(json.loads(response.content))
            regions.append(json.loads(response.content))
            parentid = json.loads(response.content)['id']
  '''       
            
           

def LoadVarietal():
    df = pd.read_csv("grapes.csv")
    grapes =[str(g).strip('\xa0').strip() for r in df['Common Name(s)'] for g in str(r).split('/')]
    varietal = [grpslug['slug'] for grpslug in GetAll("api/varietal/")]
    for grape in grapes:
        if slugify(grape) in varietal:
            continue
        response = Post("api/varietal/",payload = {'name':grape, 'slug':grape})

def LoadBlendVarietal():
    '''
    array = ['Cabernet Sauvignon', 'Red Bordeaux Blend', 'Sangiovese',
       'Pinot Noir', 'Mourvèdre', 'Syrah', 'Chardonnay',
       'Red Rhone Blend', 'Malbec', 'Cabernet Franc', 'Champagne Blend',
       'Port Blend', 'Merlot', 'Red Blend', 'Sauvignon Blanc', 'Barbera',
       'Nebbiolo', 'Sémillon-Sauvignon Blanc Blend', 'White Blend',
       'Petite Sirah', 'Albariño', 'Tinto Fino', 'Tempranillo Blend',
       'Grenache', 'Grenache Blend', 'Syrah Blend', 'Zinfandel',
       'Tempranillo', 'Gewürztraminer','Champagne','White Rhone Blend','Cava']
    '''
    db_varietal = [grpslug['slug'] for grpslug in GetAll("api/mastervarietal/")]
    mastervarietals = []
    with open("master_varietal.txt","r",encoding="utf-8") as f:
        mastervarietals = [f.strip('\n') for f in f.readlines()]
    for mblend in mastervarietals:
        if slugify(mblend) in db_varietal:
             continue
        response = Post("api/mastervarietal/",payload = {"name":mblend,"slug":mblend})
    
if __name__ == "__main__":
    print("Loading country")
    #LoadCountry()
    print("Load Regions")
    LoadRegions()
    #print("Loading varietal")
    #LoadVarietal()
    #print("Loading belnding")
    #LoadBlendVarietal()