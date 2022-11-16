import json
import boto3
import time
import requests
from package.requests_aws4auth import AWS4Auth

def lambda_handler(event, context):
    # TODO implement
    print(event)
    inputText = event['queryStringParameters']['q']
    keywords = get_keywords(inputText)
    # image_array = ['https://photosb2.s3.amazonaws.com/CatsHaveFacialExpressionsButHardToRead_600_1575488650581.jpg', 'https://photosb2.s3.amazonaws.com/191024091949-02-foster-cat-large-169_1575488572532.jpg']
    image_array = get_image_locations(keywords)
    return {
        'statusCode': 200,
        'headers':{
            'Access-Control-Allow-Origin':'*',
            'Access-Control-Allow-Credentials':True
        },
        'body': json.dumps({"results":image_array})
    }

def get_keywords(inputText):
    lex = boto3.client('lex-runtime')
    response = lex.post_text(
        botName = 'searchBot',
        botAlias = '$LATEST',
        userId = 'searchPhotosLambda',
        inputText = inputText
    )
    print(response['slots'])
    keywords = []
    slots = response['slots']
    keywords = [v for _, v in slots.items() if v]
    print(keywords)
    return keywords
    
def get_image_locations(keywords):
    endpoint = 'https://search-photo-search-phcyn7a3i6uau2hvr2hywzxs54.us-east-1.es.amazonaws.com/photo-sear/_search'
    headers = {'Content-Type': 'application/json'}
    prepared_q = []
    for k in keywords:
        prepared_q.append({"match": {"labels": k}})
    q = {"query": {"bool": {"should": prepared_q}}}
    r = requests.post(endpoint, headers=headers, data=json.dumps(q))
    print(r.json())
    # r = {"took": 7, "timed_out": False, "_shards": {"total": 5, "successful": 5, "skipped": 0, "failed": 0}, "hits": {"total": {"value": 4, "relation": "eq"}, "max_score": 1.0, "hits": [{"_index": "photos", "_type": "photo", "_id": "5uWzhW4B9mNrwci-n6la", "_score": 1.0, "_source": {"objectKey": "uploaded_photos/gettyimages-91495990-170667a.jpg", "bucket": "photosb2", "createdTimestamp": "20191119-220611", "labels": ["Plant", "Tree", "Person", "Human", "Tree Trunk", "Outdoors"]}}, {"_index": "photos", "_type": "photo", "_id": "6OW5hW4B9mNrwci-Yqk8", "_score": 1.0, "_source": {"objectKey": "uploaded_photos/scott-eastwood.jpg", "bucket": "photosb2", "createdTimestamp": "20191119-221229", "labels": ["Person", "Human", "Canine", "Dog", "Pet", "Animal", "Mammal"]}}, {"_index": "photos", "_type": "photo", "_id": "5-W0hW4B9mNrwci-ZqlW", "_score": 1.0, "_source": {"objectKey": "uploaded_photos/pjimage-43-2.jpg", "bucket": "photosb2", "createdTimestamp": "20191119-220702", "labels": ["Tree", "Christmas Tree", "Ornament", "Plant", "Human", "Person"]}}, {"_index": "photos", "_type": "photo", "_id": "5eWzhW4B9mNrwci-V6mF", "_score": 1.0, "_source": {"objectKey": "uploaded_photos/pjimage-43-2.jpg", "bucket": "photosb2", "createdTimestamp": "20191119-220553", "labels": ["Tree", "Ornament", "Christmas Tree", "Plant", "Person", "Human"]}}]}}
    
    image_array = []
    for each in r.json()['hits']['hits']:
        objectKey = each['_source']['objectKey']
        bucket = each['_source']['bucket']
        image_url = "https://" + bucket + ".s3.amazonaws.com/" + objectKey
        image_array.append(image_url)
        print(each['_source']['labels'])
    print(image_array)
    return image_array