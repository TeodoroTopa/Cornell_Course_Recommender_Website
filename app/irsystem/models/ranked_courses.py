"""
Gets the ranked list of courses based on the cosine similarity measure 
between the courses (using the subject, catalog number, title, and description 
of the courses, along with the subject and catalog number together without spaces).
"""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.irsystem.models.helpers import *
import pandas as pd
import numpy as np

class RankedCourses:
    
    def __init__(self, query):
        self.query = query


    def get_ranked_course_indices(self, tf_idf_vectorizer, all_docs_tfidf):
        """Gets the indices of the ranked courses.
        """
        query_tfidf = tf_idf_vectorizer.transform([self.query])
        sim_array = cosine_similarity(query_tfidf, all_docs_tfidf).flatten()

        sorted_indices_all = list(np.argsort(sim_array)[::-1])
        sorted_sim_array = sorted(sim_array)[::-1]  # descending order

        # only keep the indices of the courses with which the query has a 
        # cosine similarity score of cos_sim_score or higher
        cos_sim_score = 0.05
        sorted_indices = [index for i, index in enumerate(sorted_indices_all) if sorted_sim_array[i] >= cos_sim_score]
        return sorted_indices
        

def get_subj_nbr_title_desc_series(data):
    """Gets the pandas series of the course subject, catalog number, title, description combined.
    """
    subject_col = data.loc[:, 'subject']
    catalogNbr_col = data.loc[:, 'catalogNbr']
    titleLong_col = data.loc[:, 'titleLong']
    description_col = data.loc[:, 'description']

    # descriptions that correspond to classes that don't have descriptions
    description_col = description_col.fillna("Not applicable.")

    # the subject, catalogNbr, titleLong, and description put together, along with the subject and catalogNbr together without spaces
    subj_nbr_title_desc_series = (subject_col + catalogNbr_col) + " " + subject_col + " " + catalogNbr_col + " " + titleLong_col + " " + description_col

    return subj_nbr_title_desc_series

def get_tfidf_matrix(data):
    """Gets the doc term tfidf matrix, with both unigrams and bigrams.

    Each row is for the documents, which include the subject, catalog number,
    long title, and description of the course, and the last row is for the
    added query.
    """
    
    subj_nbr_title_desc_series = get_subj_nbr_title_desc_series(data)

    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    doc_term_tfidf_matrix = vectorizer.fit_transform(subj_nbr_title_desc_series)
    return [vectorizer,  doc_term_tfidf_matrix]


def get_similarity_array():
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
        

def get_ranked_course_indices():
    """Gets the indices of the ranked courses.
    """

    sim_array = self.get_similarity_array()
    sorted_indices = list(np.argsort(sim_array)[::-1])

    # number of courses to be shown as output
    num_courses = 15

    # the indices of the most similar num_courses courses to the query
    result = sorted_indices[:num_courses]
    return [course_contents[index] for index in result]


def main():
    query = "language and information"
    RankedCoursesObj = RankedCourses(query)
    course_contents = get_course_data()
    normalized_data = pd.json_normalize(course_contents)
    tf_idf_vectorizer, docs_tf = get_tfidf_matrix(normalized_data)
    ranked_course_indices = RankedCoursesObj.get_ranked_course_indices(tf_idf_vectorizer,docs_tf)
    print(ranked_course_indices)

if __name__ == "__main__":
    main()
    

