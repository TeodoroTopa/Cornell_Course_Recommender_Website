"""
Gets the ranked list of courses based on the cosine similarity measure 
between the courses (using the subject, catalog number, title, and description 
of the courses).

mcheng1
Apr 16, 2021
"""
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

class RankedCourses:
    
    def __init__(self, query, data):
        self.query = query
        self.data = pd.json_normalize(data)
        self.sorted_indeces = []  # indeces of the courses

    def get_tfidf_matrix(self):
        """Gets the doc term tfidf matrix.
        
        Each row is for the documents, which include the subject, catalog number, 
        long title, and description of the course, and the last row is for the 
        added query.
        """
        
        subject_col = self.data.loc[:,'subject']
        catalogNbr_col = self.data.loc[:,'catalogNbr']
        titleLong_col = self.data.loc[:,'titleLong']
        description_col = self.data.loc[:,'description']
        
        # descriptions that correspond to classes that don't have descriptions
        description_col = description_col.fillna("Not applicable.")

        # the subject, catalogNbr, titleLong, and description put together
        subj_nbr_title_desc_series = subject_col + " " + catalogNbr_col + " " + titleLong_col + " " + description_col

        # append query
        subj_nbr_title_desc_series = subj_nbr_title_desc_series.append(pd.Series(self.query))

        vectorizer = TfidfVectorizer(stop_words='english')

        doc_term_tfidf_matrix = vectorizer.fit_transform(subj_nbr_title_desc_series).toarray()

        return doc_term_tfidf_matrix

    def get_similarity_array(self, get_tfidf_matrix=get_tfidf_matrix):
        """Gets the similarity array.
        
        How similar the doc is to the query is determined by the cosine similarity 
        score.
        """
        
        doc_term_tfidf_matrix = get_tfidf_matrix(self)
        num_docs = len(doc_term_tfidf_matrix) - 1

        query_array = doc_term_tfidf_matrix[-1,:]
        
        sim_array = np.zeros(num_docs)  # array of similarity scores

        for i in range(num_docs):
            
            array_1 = [query_array]
            array_2 = [doc_term_tfidf_matrix[i,:]]
            
            sim_array[i] = cosine_similarity(array_1, array_2)
        
        return sim_array
        

    def get_ranked_course_indeces(self, get_similarity_array=get_similarity_array):
        """Gets the indices of the ranked courses.
        """

        sim_array = get_similarity_array(self)
        self.sorted_indeces = list(np.argsort(sim_array)[::-1])

        # number of courses to be shown as output
        num_courses = 15

        # the indices of the most similar num_courses courses to the query
        return self.sorted_indeces[:num_courses]
        

def main():

    f = open("../../../preliminary_scraping/with_roster_api/course_data")
    data = json.load(f)
    query = "language and information"
    RankedCoursesObj = RankedCourses(query, data)
    ranked_course_indeces = RankedCoursesObj.get_ranked_course_indeces()
    print(ranked_course_indeces)

if __name__ == "__main__":
    main()
    

