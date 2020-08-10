import pandas as pd
import requests, json, socket
from requests.exceptions import HTTPError
from requests.auth import HTTPBasicAuth
from django.utils.text import slugify

URL = f'http://{socket.gethostname()}:8000'

class WBase():
     def __init__(self, country):
          self.id = 0
          self.country = country

     def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

class Terroir(WBase):
    def __init__(self, name, parentterroir=None, isappelation=False, isvineyard=False, country=None):
        self.name = name
        self.parentterroir = parentterroir
        self.isappelation = isappelation
        self.isvineyard = isvineyard
        super().__init__(country)

class Market():
    def __init__(self,year,price,review=None, purchaseddate=None):
        self.vintage = year
        self.price = price
        self.review = review
        self.purchasedon = purchaseddate

class Wine():
    def __init__(self,**kargs):
        self.name = kargs['wineinfo'].Wine
        self.country = kargs['wineinfo'].Country
        self.region = kargs['wineinfo'].Region
        self.subregion = kargs['wineinfo'].SubRegion
        self.appellation = kargs['wineinfo'].Appellation        
        self.vineyard = kargs['wineinfo'].Vineyard
        self.designation = kargs['wineinfo'].Designation 
        self.market = Market(kargs['wineinfo'].Vintage,kargs['wineinfo'].Price)  
        self.mainvarietal = kargs['wineinfo'].MasterVarietal
        self.iwineid = kargs['wineinfo'].iWine

class Producer():
    def __init__(self, **kargs):
        self.name = kargs['name']
        self.wines = [Wine(wineinfo=wine) for key,wine in kargs['wines'].iterrows()]

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
    return response
    #jsonResponse = response.json()
    #print(jsonResponse)

region_mapping = [
('California','USA'),
('Maipo Valley','CHL'),
('Tuscany','ITA'),
('Burgundy','FRA'),
('Bordeaux','FRA'),
('Rhône','FRA'),
('Oregon','USA'),
('Washington','USA'),
('Mendoza','ARG'),
('Champagne','FRA'),
('Douro','PRT'),
('Piedmont','ITA'),
('Cognac','FRA'),
('Rapel Valley','CHL'),
('Galicia','ESP'),
('Castilla y Léon','ESP'),
('La Rioja','ESP'),
('South Australia','AUS'),
('Catalunya','ESP'),
('Alsace','FRA')]

df = pd.read_csv("mycellar.csv", encoding="iso8859_15")
for producer,wines in df.groupby(["Producer"]):
    wine = Producer(name=producer,wines=wines)

payload = []
for terroir, wines in df.groupby(['Region']):
    
    countryid = [r for r in region_mapping if slugify(r[0])== slugify(terroir)][0]
    country = Get(f'api/country/{countryid[1]}')
    print(f"Region: {terroir} [{country['id']}]")
    region = Terroir(terroir, country=country['id'])
    response = Post("api/terroir/",payload = json.loads(region.toJson()))
    response_data = json.loads(response.text)
    region.id = response_data['id']

    #Get all subregions associate to..
    regionalwines = [(subregion,regionwines) for subregion, regionwines in wines.groupby(['SubRegion'])]
    
    for subregion in regionalwines:
        print(f"SubRegion: {subregion[0]}")
        subregionterroir = 0
        checkregion = Get(f"api/terroir/{slugify(subregion[0])}")
        if checkregion is None:
            subregionterroir = Terroir(name=subregion[0],parentterroir=region.id,country=country['id'])
            resp  = Post("api/terroir/",payload = json.loads(subregionterroir.toJson()))
            respdata = json.loads(resp.text)
            subregionterroir.id = respdata['id']
        else:
            subregionterroir = checkregion

        appellation_tuples = [(appelation,appellationines) for appelation, appellationines in subregion[1].groupby(['Appellation'])]

        for appelation in appellation_tuples:
            print(f"Appelation: {appelation[0]}")
            check = Get(f"api/terroir/{slugify(subregion[0])}")
            
            if check is None:
                appelationterroir = Terroir(name=appelation[0],parentterroir=subregionterroir.id, isappelation=True, country=country['id'])
                if appelation[0] != "Unknown":
                    resp  = Post("api/terroir/",payload = json.loads(appelationterroir.toJson()))
                    respdata = json.loads(resp.text)
                    appelationterroir.id = respdata['id']
                else:
                    appelationterroir.id = subregionterroir.id
            else:
                appelationterroir = check

            vineyard_tuples = [(vineyard,vineyardwines) for vineyard, vineyardwines in appelation[1].groupby(['Vineyard'])]

            for vineyard in vineyard_tuples:
                print(f"Vineyard: {vineyard[0]}")
                check = Get(f"api/terroir/{slugify(vineyard[0])}")
                if check is None and vineyard[0] != "Unknown":
                    vineyardterroir = Terroir(name=vineyard[0],parentterroir=appelationterroir['id'], isvineyard=True,country=country['id'])
                    resp  = Post("api/terroir/",payload = json.loads(vineyardterroir.toJson()))
                    respdata = json.loads(resp.text)

    """
    for sr in [r for r in regionalwines]:
        srname = tuple(sr)[0]
        subregion = Terroir(name=srname,parentterroir=response_data['id'])
        resp  = Post("api/terroir/",payload = json.loads(subregion.toJson()))
        respdata = json.loads(resp.text)
        subregion.id = respdata['id']
        appellation = None
        vineyard = None
        if (tuple(sr)[1]).Appellation.values[0] != "Unknown":
            appellation = Terroir((tuple(sr)[1]).Appellation.values[0], respdata['id'],isappelation=True)
            resp  = Post("api/terroir/",payload = json.loads(appellation.toJson()))
            appellation.id = json.loads(resp.text)['id']

        if (tuple(sr)[1]).Vineyard.values[0] != "Unknown":
            vineyard = Terroir( (tuple(sr)[1]).Vineyard.values[0], 
                                [subregion.id if appellation == None else appellation.id], 
                                isvineyard=True)
            Post("api/terroir/",payload = json.loads(vineyard.toJson()))
        """