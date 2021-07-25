import boto3
import json
import requests
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection
import os

YELP_API_KEY = os.environ.get('YELP_API_KEY')

ENDPOINT = "https://api.yelp.com/v3/businesses/search"
HEADERS = {'Authorization': 'bearer %s' % YELP_API_KEY}
business_data = []
offset = 0
for _ in range(20):
    PARAMETERS = {'term': 'mexican restaurant', 'categories':'restaurants,mexican', 'offset': offset, 'limit': 50, 'location': 'New York City'}
    response = requests.get(url = ENDPOINT, params= PARAMETERS, headers= HEADERS)
    newdata = response.json()
    print(newdata)
    newdata = newdata['businesses']
    business_data += newdata
    offset += 50

with open("finalmexicanyelpfile.json", "w") as write_file:
    json.dump(business_data, write_file)