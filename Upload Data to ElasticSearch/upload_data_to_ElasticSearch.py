from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import json
import boto3
import os

credentials = boto3.Session(aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID'), aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')).get_credentials()

region = 'us-east-1'
service = 'es'

awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
host = 'search-yelp-restaurants-pi5uu6x2lzpdmtdrtbchj4wkju.us-east-1.es.amazonaws.com'

print(awsauth)

es = Elasticsearch(
	hosts = [{'host': host, 'port': 443}],
	http_auth = awsauth,
	use_ssl = True,
	verify_certs = True,
	connection_class = RequestsHttpConnection
	)


def elasticInsert(restaurants):

    for restaurant in restaurants:

        dataObject = {
            'id': restaurant['id'],
            'categories': restaurant['categories']
        }

        print('dataObject', dataObject)
        es.index(index="restaurants", doc_type="Restaurant", id=dataObject['id'], body=dataObject, refresh=True)
        print(es.get(index="restaurants", doc_type="Restaurant", id=dataObject['id']))
        return

cuisines = ['indian', 'chinese', 'italian', 'mexican', 'korean', 'thai', 'japanese']
for i in range(7):
    filename = 'final' + cuisines[i] + 'yelpfile.json'
    f = open(filename) 
    data = json.load(f)
    elasticInsert(data)