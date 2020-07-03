import requests, json
from requests.exceptions import HTTPError
from requests.auth import HTTPBasicAuth
import pandas as pd
import re

URL = 'http://127.0.0.1:8000'

def Get(page):
    try:
        response = requests.get(f"{URL}/{page}")
        response.raise_for_status()
        # access JSOn content
        jsonResponse = response.json()
        print("Entire JSON response")
        print(jsonResponse)

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

def Post(page, **kargs):
    headers = {'content-type': 'application/json'}
    response = requests.post(f"{URL}/{page}" , auth=HTTPBasicAuth('admin','password123'), data=json.dumps(kargs["payload"]), headers=headers)
    jsonResponse = response.json()
    print(jsonResponse)

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
                        }]
                   }
        dataset["wines"].append(wineset)
    Post("api/wine/",payload = dataset)
    break


#Get("api/wine/")

"""
Post('producers',name="Duckhorn2", wines=
    [
        {
            "name":"name1",
            "country":"FRA",
            "region":"region1",
            "terroir":"terroir1",
            "vintage":[
                    { 
                        "price" : "2050.99",
                        "year" : "2017",
                        "reviews" : [
                                        {
                                            "issuedate":"2020-01-01",
                                            "observation" : "Hello World",
                                            "score" : "100"           
                                        }
                ]
                    }
                ]
            }
    ])    
"""