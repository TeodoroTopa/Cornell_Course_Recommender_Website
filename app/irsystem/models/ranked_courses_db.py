
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
# import boto3
# import botocore
# from botocore import UNSIGNED
# from botocore.config import Config

# course_contents = []
# normalized_data  = Non
    
# def __init__(self, query):
#     global course_contents, normalized_data

#     self.query = query
#     if len(course_contents)==0:
#         print ("ahhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
#         self.get_course_data()
#     if normalized_data is None: # main point of concern would be normalizing with pandas
#         normalized_data = pd.json_normalize(course_contents)
#     self.sorted_indeces = []  # indeces of the courses

# can substitute this out by performing a DB query
# may require code refactoring to switch over from json formatting to DB formatting (tuples)
# def get_course_data(self):

#     BUCKET_NAME = 'cornell-course-data-bucket'
#     PATH = 'course_data.json'
#     global course_contents

#     s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED))
#     try:
#         content_object = s3.Object(BUCKET_NAME, PATH)
#         file_content = content_object.get()['Body'].read().decode('utf-8')
#         course_contents = json.loads(file_content)
#     except botocore.exceptions.ClientError as e:
#         if e.response['Error']['Code'] == "404":
#             print("The object does not exist.")
#         else:
#             raise

''' connect to database '''
''' note that these credentials may need to change '''
DATABASE_URL = os.environ['DATABASE_URL']
DB_NAME = "d79u63b2cbg9om"
DB_PORT = 5432
DB_USER = "kugnzgerojalup"
DB_PASS = "f4c347af5b4f5818e118cf656221324546d81dd0c539cd588f9f80e9bf7ecdc9"
DB_HOST = "ec2-54-211-176-156.compute-1.amazonaws.com"

conn = psycopg2.connect(dbname=DB_NAME, port=DB_PORT, user=DB_USER, password=DB_PASS, host=DB_HOST)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

''' NOTE: do not forget to [heroku login] before starting '''

''' creating a cursor object '''
cur = conn.cursor()

class DB_Access:
    def get_tfidf_matrix(self):
        """Gets the doc term tfidf matrix.
        
        Each row is for the documents, which include the subject, catalog number, 
        long title, and description of the course, and the last row is for the 
        added query.
        """
        # global normalized_data

        # subject_col = normalized_data.loc[:,'subject']
        # catalogNbr_col = normalized_data.loc[:,'catalogNbr']
        # titleLong_col = normalized_data.loc[:,'titleLong']
        # description_col = normalized_data.loc[:,'description']

        # descriptions that correspond to classes that don't have descriptions
        # description_col = description_col.fillna("Not applicable.")

        global cur, conn
        cur.execute('''SELECT subject FROM CLASS''')
        subject_col = cur.fetchall()
        conn.commit()

        cur.execute('''SELECT catalogNbr FROM CLASS''')
        catalogNbr_col = cur.fetchall()
        conn.commit()

        cur.execute('''SELECT titleLong FROM CLASS''')
        titleLong_col = cur.fetchall()
        conn.commit()

        cur.execute('''SELECT description FROM CLASS''')
        description_col = cur.fetchall()
        conn.commit()

        # the subject, catalogNbr, titleLong, and description put together
        subj_nbr_title_desc_series = subject_col + " " + catalogNbr_col + " " + titleLong_col + " " + description_col

        # append query
        subj_nbr_title_desc_series = subj_nbr_title_desc_series.append(pd.Series(self.query))

        vectorizer = TfidfVectorizer(stop_words='english')

        return vectorizer.fit_transform(subj_nbr_title_desc_series).toarray()


