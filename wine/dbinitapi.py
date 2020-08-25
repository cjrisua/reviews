import requests, json, re
from requests.exceptions import HTTPError
from requests.auth import HTTPBasicAuth
import pandas as pd
import socket
from django.utils.text import slugify

URL = f'http://{socket.gethostname()}:8000'

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
    r = Get(f"{page}?page=1")
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
            ('ZAF', 'South Africa'),)
    countries = [{"name": name, "abbreviation": abbreviation} for abbreviation, name in countries]
    for country in countries:
        response = Post("api/country/",payload = country)

def LoadVarietal():
    df = pd.read_csv("grapes.csv")
    grapes =[str(g).strip('\xa0').strip() for r in df['Common Name(s)'] for g in str(r).split('/')]
    varietal = [grpslug['slug'] for grpslug in GetAll("api/varietal/")]
    for grape in grapes:
        if slugify(grape) in varietal:
            continue
        response = Post("api/varietal/",payload = {'name':grape, 'slug':grape})

def LoadBlendVarietal():

    array = ['Cabernet Sauvignon', 'Red Bordeaux Blend', 'Sangiovese',
       'Pinot Noir', 'Mourvèdre', 'Syrah', 'Chardonnay',
       'Red Rhone Blend', 'Malbec', 'Cabernet Franc', 'Champagne Blend',
       'Port Blend', 'Merlot', 'Red Blend', 'Sauvignon Blanc', 'Barbera',
       'Nebbiolo', 'Sémillon-Sauvignon Blanc Blend', 'White Blend',
       'Petite Sirah', 'Albariño', 'Tinto Fino', 'Tempranillo Blend',
       'Grenache', 'Grenache Blend', 'Syrah Blend', 'Zinfandel',
       'Tempranillo', 'Gewürztraminer','Champagne','White Rhone Blend','Cava']
    
    response = Get(f"api/varietal/none/")
    if response is None:
        response = Post("api/varietal/",payload = {"name":"None","slug":"none"})
    default_varietalid = response['id']

    for blendname in array:
        response = Get(f"api/varietal/{slugify(blendname)}/")
        if response is not None:
            varietalid = response['id']
        else:
            varietalid = default_varietalid

        response = Post("api/blendvarietal/",payload = 
            {"name": blendname ,
             "varietal": [
                
                    varietalid
                
            ]})

if __name__ == "__main__":
    print("Loading country")
    #LoadCountry()
    print("Loading varietal")
    LoadVarietal()
    print("Loading belnding")
    #LoadBlendVarietal()