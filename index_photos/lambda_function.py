import json
import boto3
import time
from botocore.vendored import requests
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

def lambda_handler(event, context):
    # TODO implement
    print(event)
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        photokey = record['s3']['object']['key']
        print(bucket, photokey)
        labels = []
        labels = get_photo_labels(bucket, photokey)
        new_doc = {
            "objectKey": photokey,
            "bucket": bucket,
            "createdTimestamp": time.strftime("%Y%m%d-%H%M%S"),
            "labels": labels
        }
        index_into_es('photos','photo',json.dumps(new_doc))
    return {
        'statusCode': 200,
        'body': json.dumps('Successful indexing')
    }
    
def get_photo_labels(bucket, photokey):
    rekClient = boto3.client('rekognition')
    response = rekClient.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photokey}}, MaxLabels=10, MinConfidence=90)
    print(response)
    # response = {"Labels": [{"Name": "Pet", "Confidence": 92.20275115966797, "Instances": [], "Parents": [{"Name": "Animal"}]}, {"Name": "Mammal", "Confidence": 92.20275115966797, "Instances": [], "Parents": [{"Name": "Animal"}]}, {"Name": "Cat", "Confidence": 92.20275115966797, "Instances": [{"BoundingBox": {"Width": 0.8125336766242981, "Height": 0.9812089204788208, "Left": 0.06638608127832413, "Top": 0.015779059380292892}, "Confidence": 89.06988525390625}], "Parents": [{"Name": "Pet"}, {"Name": "Mammal"}, {"Name": "Animal"}]}, {"Name": "Animal", "Confidence": 92.20275115966797, "Instances": [], "Parents": []}, {"Name": "Abyssinian", "Confidence": 89.86946105957031, "Instances": [], "Parents": [{"Name": "Pet"}, {"Name": "Cat"}, {"Name": "Mammal"}, {"Name": "Animal"}]}, {"Name": "Manx", "Confidence": 85.65826416015625, "Instances": [], "Parents": [{"Name": "Pet"}, {"Name": "Cat"}, {"Name": "Mammal"}, {"Name": "Animal"}]}, {"Name": "Angora", "Confidence": 57.59444046020508, "Instances": [], "Parents": [{"Name": "Pet"}, {"Name": "Cat"}, {"Name": "Mammal"}, {"Name": "Animal"}]}], "LabelModelVersion": "2.0", "ResponseMetadata": {"RequestId": "4b3dd7c5-e13f-4740-b96f-f169949af26b", "HTTPStatusCode": 200, "HTTPHeaders": {"content-type": "application/x-amz-json-1.1", "date": "Tue, 19 Nov 2019 15:53:53 GMT", "x-amzn-requestid": "4b3dd7c5-e13f-4740-b96f-f169949af26b", "content-length": "1009", "connection": "keep-alive"}, "RetryAttempts": 0}}
    print(response['Labels'])
    labels = [label['Name'] for label in response['Labels']]
    print(labels)
    return labels

def index_into_es(index, type_doc, new_doc):

    host = 'search-photo-search-phcyn7a3i6uau2hvr2hywzxs54.us-east-1.es.amazonaws.com'
    credential = boto3.Session(region_name="us-east-1").get_credentials()
    region = 'us-east-1'
    service = 'es'
    auth = AWS4Auth(credential.access_key, credential.secret_key, region, service)

    es = Elasticsearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = auth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection   
    )
    print(es)

    es.index(index=index, doc_type=type_doc, body=new_doc)