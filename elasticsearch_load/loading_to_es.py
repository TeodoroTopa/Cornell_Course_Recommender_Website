# This is the file I  used to load our course data to Elasticsearch
# Note; please do not run this unless you actually need to load data :D
# At risk of overwriting existing ES data

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import boto3
import botocore
from botocore import UNSIGNED
from botocore.config import Config
import json
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch import helpers

BUCKET_NAME = 'cornell-course-data-bucket'
PATH = 'course_data.json'

s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED))
json_content = []

try:
	content_object = s3.Object(BUCKET_NAME, PATH)
	file_content = content_object.get()['Body'].read().decode('utf-8')
	json_content = json.loads(file_content)
except botocore.exceptions.ClientError as e:
	if e.response['Error']['Code'] == "404":
		print("The object does not exist.")
	else:
		raise

DATABASE_URL = os.environ['DATABASE_URL']
DB_NAME = "d79u63b2cbg9om"
DB_PORT = 5432
DB_USER = "kugnzgerojalup"
DB_PASS = "f4c347af5b4f5818e118cf656221324546d81dd0c539cd588f9f80e9bf7ecdc9"
DB_HOST = "ec2-54-211-176-156.compute-1.amazonaws.com"

conn = psycopg2.connect(dbname=DB_NAME, port=DB_PORT, user=DB_USER, password=DB_PASS, host=DB_HOST)
cur = conn.cursor()
x =  cur.execute("SELECT *  FROM class")
x2 = cur.fetchall()
cols = [desc[0] for desc in cur.description]

for x in json_content:
	dropcols =  [c for c in list(x.keys()) if c.lower() not in cols]
	dr = [x.pop(key) for key in dropcols]

es = Elasticsearch(
    hosts= "search-cornellcourserecommender-sqp7dbsc4owlrftw5cefn7lfjq.us-east-1.es.amazonaws.com",
    http_auth=("courserecs", "Cornell2021!"),
    port=443,
    use_ssl=True,
    connection_class=RequestsHttpConnection,
    scheme="https"
)

actions = [
    {
    "_index" : "roster",
    "_type" : "external",
    "_id" : course['classNbr'],
    "_source" : course
    }
for course in json_content
]

helpers.bulk(es,actions)