import pandas as pd
import requests, json, socket
from requests.exceptions import HTTPError
from requests.auth import HTTPBasicAuth
#from django.utils.text import slugify
from slugify import Slugify, UniqueSlugify, slugify, slugify_unicode

URL = f'http://{socket.gethostname()}:3000'

slugify = Slugify()
slugify.to_lower = True
slugify.pretranslate ={'.':'','&':'and'}

data = {}

def Get(page):
    try:
        response = requests.get(f"{URL}/{page}")
        response.raise_for_status()
        # access JSOn content
        return response.json() 
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    
    return {'error':404}

def Post(page, **kargs):
    headers = {'content-type': 'application/json'}
    response = requests.post(f"{URL}/{page}" , auth=HTTPBasicAuth('admin','password123'), data=json.dumps(kargs["payload"]), headers=headers)
    return response


def LoadData(dataset,model):
    global data
    data[model] =[]
    for dsitem in dataset:
        result = Get(f"api/{model}?slug={slugify(dsitem['name'])}")
        if 'error' in result:
           payload = {}
           if model == 'Wine':
               mastervarietalId =  [l for l in data['MasterVarietal'] if l['slug'] == slugify(dsitem['mastervarietal']) ][0]
               region =  [l for l in data['Region'] if l['slug'] == slugify(dsitem['region']) ][0]
               subregion =  [l for l in data['Region'] if l['slug'] == slugify(dsitem['subregion']) ][0]
               appellation =  [l for l in data['Region'] if l['slug'] == slugify(dsitem['appellation']) ][0]
               producerId =  [l for l in data['Producer'] if l['slug'] == slugify(dsitem['producer']) ][0]
               payload['mastervarietalId'] = mastervarietalId['id']
               payload['regionId'] = appellation['id'] if appellation['slug'] != "unknown" else subregion['id'] if subregion['slug'] != 'unknown' else region['id']
               payload['producerId'] = producerId['id']
               payload['name'] =slugify(dsitem['name'])
               
               Post(f"api/{model}",payload=payload)

           elif model == 'Region':
               print("region")
               pass
           elif model == 'Vintage':
               wine =  [l for l in data['Wine'] if l['slug'] == slugify(dsitem['name']) ][0]
               print(wine) 

        elif model != 'Vintage':
            data[model].append({'id':result[0]['id'], 'slug':slugify(dsitem['name'])})

df=pd.read_csv("MyCellar.csv",encoding='latin1')

dataset={}
dataset['Country'] = [{'name':d} for d in list(set([p for p in df['Country']]))]
LoadData(dataset['Country'],'Country')

dataset['Region'] = [{'name':p[0][0]} for p in df.groupby(['Region','Country'])]
[dataset['Region'].append({'name':p[0][0]}) for p in df.groupby(['SubRegion','Country'])]
[dataset['Region'].append({'name':p[0][0]}) for p in df.groupby(['Appellation','Country'])]
LoadData(dataset['Region'],'Region')

#dataset['SubRegion'] = [{'name':p[0][0]} for p in df.groupby(['SubRegion','Country'])]
LoadData(dataset['Region'],'Region')

dataset['Producer'] = [{'name':d} for d in list(set([p for p in df['Producer']]))]
LoadData(dataset['Producer'],'Producer')

dataset['MasterVarietal'] = [{'name':d, 'varieties':[]} for d in list(set([p for p in df['MasterVarietal']]))]
LoadData(dataset['MasterVarietal'],'MasterVarietal')

dataset['Wine'] = [{'name':p[0][0],'mastervarietal':p[0][1], 'appellation':p[0][2] ,'country':p[0][3],'producer':p[0][4],'region':p[0][5],'subregion':p[0][6]} for p in df.groupby(['Producer','MasterVarietal','Appellation','Country','Producer','Region','SubRegion'])]
LoadData(dataset['Wine'],'Wine')

dataset['Vintage'] = [{'name':p[0][0],'year':p[0][7]} for p in df.groupby(['Producer','MasterVarietal','Appellation','Country','Producer','Region','SubRegion','Vintage'])]
LoadData(dataset['Vintage'],'Vintage')