# Methods to compose HTTP response JSON 
from flask import jsonify
import base64
import json
import numpy as np
import boto3
import botocore
from botocore import UNSIGNED
from botocore.config import Config
from sklearn.feature_extraction.text import TfidfVectorizer
from io import BytesIO
import os
import pickle
import datetime

def http_json(result, bool):
	result.update({ "success": bool })
	return jsonify(result)


def http_resource(result, name, bool=True):
	resp = { "data": { name : result }}
	return http_json(resp, bool)


def http_errors(result): 
	errors = { "data" : { "errors" : result.errors["_schema"] }}
	return http_json(errors, False)

class NumpyEncoder(json.JSONEncoder):

    def default(self, obj):
        """If input object is an ndarray it will be converted into a dict 
        holding dtype, shape and the data, base64 encoded.
        """
        if isinstance(obj, np.ndarray):
            if obj.flags['C_CONTIGUOUS']:
                obj_data = obj.data
            else:
                cont_obj = np.ascontiguousarray(obj)
                assert(cont_obj.flags['C_CONTIGUOUS'])
                obj_data = cont_obj.data
            data_b64 = base64.b64encode(obj_data)
            return dict(__ndarray__=data_b64,
                        dtype=str(obj.dtype),
                        shape=obj.shape)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder(self, obj)
        
def json_numpy_obj_hook(dct):
    """Decodes a previously encoded numpy ndarray with proper shape and dtype.
    :param dct: (dict) json encoded ndarray
    :return: (ndarray) if input was an encoded ndarray
    """
    if isinstance(dct, dict) and '__ndarray__' in dct:
        data = base64.b64decode(dct['__ndarray__'])
        return np.frombuffer(data, dct['dtype']).reshape(dct['shape'])
    return dct


def get_course_data():
    BUCKET_NAME = 'cornell-course-data-bucket'
    PATH = 'course_data_2021fall.json'

    s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED))
    try:
        content_object = s3.Object(BUCKET_NAME, PATH)
        file_content = content_object.get()['Body'].read().decode('utf-8-sig')
        return json.loads(file_content)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
        return []

    # BUCKET_NAME = 'cornell-course-data-bucket'
    # s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED))
    
    # date = datetime.date.today()
    # date_yr = date.year
    # date_month = date.month
    # date_day = date.day
    # sub = -999

    # PATHS = []
    # if (date_month >= 3 and date_day >= 20):
    #     sub = (str)(date_yr)[2:]
    # else:
    #     sub = (str)(date_yr - 1)[2:]
    # PATHS.append('course_data_FA' + str(sub) + "_pt1.json")
    # # PATHS.append('course_data_FA' + str(sub) + "_pt2.json")

    # try:
    #     print ("help!")
    #     content_object_0 = s3.Object(BUCKET_NAME, PATHS[0])
    #     file_content_0 = content_object_0.get()['Body'].read().decode('utf-8-sig')
    #     ret0 = json.loads(file_content_0)
    #     # content_object_1 = s3.Object(BUCKET_NAME, PATHS[1])
    #     # file_content_1 = content_object_1.get()['Body'].read().decode('utf-8-sig')
    #     # ret1 = json.loads(file_content_1)

    #     return ret0
    #     # return ret0+ret1

    except botocore.exceptions.ClientError as e:
        print ("help!!!!!!!!")
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
        return []



def get_svm_data(picklepath = "docs_compressed.pkl"):
    BUCKET_NAME = 'cornell-course-data-bucket'

    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    with BytesIO() as data:
        s3.download_fileobj(BUCKET_NAME, picklepath, data)
        data.seek(0)
        loaded = pickle.load(data)

    return loaded
