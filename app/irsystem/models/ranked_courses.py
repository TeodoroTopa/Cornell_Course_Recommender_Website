"""
Gets the ranked list of courses based on the cosine similarity measure 
between the courses (using the subject, catalog number, title, and description 
of the courses).
"""
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import boto3
import botocore
from botocore import UNSIGNED
from botocore.config import Config

course_contents = []
normalized_data  = None

class RankedCourses:
    
    def __init__(self, query):
        global course_contents, normalized_data

        self.query = query
        if len(course_contents)==0:
            print ("ahhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
            self.get_course_data()
        if normalized_data is None:
            normalized_data = pd.json_normalize(course_contents)
        self.sorted_indeces = []  # indeces of the courses

    # can substitute this out by performing a DB query
    # may require code refactoring to switch over from json formatting to DB formatting (tuples)
    def get_course_data(self):

        BUCKET_NAME = 'cornell-course-data-bucket'
        PATH = 'course_data.json'
        global course_contents

        s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED))
        try:
            content_object = s3.Object(BUCKET_NAME, PATH)
            file_content = content_object.get()['Body'].read().decode('utf-8')
            course_contents = json.loads(file_content)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise

    def get_tfidf_matrix(self):
        """Gets the doc term tfidf matrix.
        
        Each row is for the documents, which include the subject, catalog number, 
        long title, and description of the course, and the last row is for the 
        added query.
        """
        global normalized_data
        subject_col = normalized_data.loc[:,'subject']
        catalogNbr_col = normalized_data.loc[:,'catalogNbr']
        titleLong_col = normalized_data.loc[:,'titleLong']
        description_col = normalized_data.loc[:,'description']
        
        # descriptions that correspond to classes that don't have descriptions
        description_col = description_col.fillna("Not applicable.")

        # the subject, catalogNbr, titleLong, and description put together
        subj_nbr_title_desc_series = subject_col + " " + catalogNbr_col + " " + titleLong_col + " " + description_col

        # append query
        subj_nbr_title_desc_series = subj_nbr_title_desc_series.append(pd.Series(self.query))

        vectorizer = TfidfVectorizer(stop_words='english')

        return vectorizer.fit_transform(subj_nbr_title_desc_series).toarray()

    def get_similarity_array(self):
        """Gets the similarity array.
        
        How similar the doc is to the query is determined by the cosine similarity 
        score.
        """

        tf_idf = self.get_tfidf_matrix()

        num_docs = len(tf_idf) - 1

        query_array = tf_idf[-1,:]
        
        sim_array = np.zeros(num_docs)  # array of similarity scores
        array_1 = [query_array]

        for i in range(num_docs):
            
            array_2 = [tf_idf[i,:]]
            
            sim_array[i] = cosine_similarity(array_1, array_2)
        
        return sim_array
        

    def get_ranked_course_indeces(self):
        """Gets the indices of the ranked courses.
        """

        sim_array = self.get_similarity_array()
        self.sorted_indeces = list(np.argsort(sim_array)[::-1])

        # number of courses to be shown as output
        num_courses = 15

        # the indices of the most similar num_courses courses to the query
        result = self.sorted_indeces[:num_courses]
        return [course_contents[index] for index in result]
        

def main():
    query = "language and information"
    RankedCoursesObj = RankedCourses(query)
    ranked_course_indeces = RankedCoursesObj.get_ranked_course_indeces()
    print(ranked_course_indeces)

if __name__ == "__main__":
    main()
    

