import requests, json
from requests.exceptions import HTTPError
from requests.auth import HTTPBasicAuth
import pandas as pd

URL = 'http://tokalon.fios-router.home:8000'

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

def Post(page, **kargs):
    headers = {'content-type': 'application/json'}
    return requests.post(f"{URL}/{page}" , auth=HTTPBasicAuth('admin','password123'), data=json.dumps(kargs["payload"]), headers=headers)
    

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

df = pd.read_csv("grapes.csv")
grapes =[str(g).strip('\xa0').strip() for r in df['Common Name(s)'] for g in str(r).split('/')]
for grape in grapes:
    response = Post("api/varietal/",payload = {'name':grape, 'slug':grape})
