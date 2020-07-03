import requests, json
from requests.exceptions import HTTPError
from requests.auth import HTTPBasicAuth

URL = 'http://127.0.0.1:8000'

def Get(page):
    try:
        URL = 'http://127.0.0.1:8000/producers/'
        response = requests.get(URL)
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
    payload = kargs
    print(f"{payload}")
    response = requests.post(str(f"{URL}/{page}/") , auth=HTTPBasicAuth('admin','password123'), data=json.dumps(payload), headers=headers)
    #jsonResponse = response.json()
    #print(jsonResponse)


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