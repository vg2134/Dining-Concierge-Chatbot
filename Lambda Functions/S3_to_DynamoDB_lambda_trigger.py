import json
import boto3
import datetime

s3_client = boto3.client('s3')

def dynamoInsert(restaurants):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('yelp-restaurants')


    for each_restaurants in restaurants:

        dataObject = {
            'id': each_restaurants['id'],
            'name': each_restaurants['name'],
            'display_address': each_restaurants['location']['display_address'][:-1],
            'review_count': each_restaurants['review_count'],
            'rating': int(each_restaurants['rating']),
        }

        
        if (each_restaurants['coordinates'] and each_restaurants['coordinates']['latitude'] and each_restaurants['coordinates']['longitude']):
            dataObject['latitude'] = str(each_restaurants['coordinates']['latitude'])
            dataObject['longitude'] = str(each_restaurants['coordinates']['longitude'])

        if (each_restaurants['location']['zip_code']):
            dataObject['zip_code'] = each_restaurants['location']['zip_code']


        print('dataObject', dataObject)
        table.put_item(
               Item={
                   'insertedAtTimestamp': str(datetime.datetime.now()),
                   'info': dataObject,
                   'id': dataObject['id']
               }
            )


def lambda_handler(event, context):
    # TODO implement
    bucket = event['Records'][0]['s3']['bucket']['name']
    json_file = event['Records'][0]['s3']['object']['key']
    json_object = s3_client.get_object(Bucket=bucket, Key=json_file)
    jsonFileReader = json_object['Body'].read()
    jsonDict = json.loads(jsonFileReader)
    dynamoInsert(jsonDict)
