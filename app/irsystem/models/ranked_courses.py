"""
Gets the ranked list of courses based on the cosine similarity measure 
between the courses (using the subject, catalog number, title, and description 
of the courses).
"""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.irsystem.models.helpers import *
import pandas as pd

class RankedCourses:
    
    def __init__(self, query):
        self.query = query


    def get_ranked_course_indeces(self, tf_idf_vectorizer, all_docs_tfidf):
        """Gets the indices of the ranked courses.
        """
        query_tfidf = tf_idf_vectorizer.transform([self.query])
        sim_array = cosine_similarity(query_tfidf, all_docs_tfidf).flatten()

        self.sorted_indeces = list(np.argsort(sim_array)[::-1])
        return self.sorted_indeces
        

def main():
    query = "language and information"
    RankedCoursesObj = RankedCourses(query)
    course_contents = get_course_data()
    normalized_data = pd.json_normalize(course_contents)
    tf_idf_vectorizer, docs_tf = get_tfidf_matrix(normalized_data)
    ranked_course_indeces = RankedCoursesObj.get_ranked_course_indeces(tf_idf_vectorizer,docs_tf)
    print(ranked_course_indeces)

if __name__ == "__main__":
    main()
    

