"""
Gets the ranked list of courses based on the cosine similarity measure 
between the courses (using the subject, catalog number, title, and description 
of the courses).
"""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.irsystem.models.helpers import *
import pandas as pd
import numpy as np
from nltk.metrics import distance

class RankedCourses:
    
    def __init__(self, query):
        self.query = query


    def get_list_and_query(self, data):
        """Gets the subject and catalog number series and the no-whitespaces query.
        """
        subject_col = data.loc[:, 'subject']
        catalogNbr_col = data.loc[:, 'catalogNbr']
        
        subject_catalogNbr_series = subject_col + catalogNbr_col

        query_no_whitespaces = "".join(self.query.split())
        
        return (subject_catalogNbr_series, query_no_whitespaces)


    def put_space_in_subj_catNbr_query(self, data):
        """If the query is of the subject and catalog number, with no spaces in between,
        then it is transformed into the subject and catalog number with a space in between.
        """
        subject_col = data.loc[:, 'subject']
        catalogNbr_col = data.loc[:, 'catalogNbr']

        (subject_catalogNbr_series, query_no_whitespaces) = self.get_list_and_query(data)

        for i, subject_catalogNbr in enumerate(subject_catalogNbr_series):
            if query_no_whitespaces == subject_catalogNbr:

                if self.query == (subject_col[i] + catalogNbr_col[i]):
                    
                    self.query = subject_col[i] + " " + catalogNbr_col[i]
    

    def check_query_if_subj_course_num(self, sim_array, data):
        """Checks if the query is the subject and the catalog number put together, 
        whether or not there is a space between them.
        """
        (subject_catalogNbr_series, query_no_whitespaces) = self.get_list_and_query(data)
        
        for i, subject_catalogNbr in enumerate(subject_catalogNbr_series):
            if query_no_whitespaces == subject_catalogNbr:
                
                sim_array[i] = 1
        
        return sim_array
    

    def misspelling_edit_distance(self, data):
        """Converts the query into the course title that has the smallest 
        edit distance with the query if the query might be of a course title 
        that is slightly misspelled.
        """
        titleLong_col = data.loc[:, 'titleLong']

        edit_dists = np.zeros(len(titleLong_col))
        for i, titleLong in enumerate(titleLong_col):

            edit_dists[i] = distance.edit_distance(self.query, titleLong)
            

        min_edit_dist = np.min(edit_dists)
        min_edit_dist_index = np.argmin(edit_dists)
        
        min_edit_dist_threshold = len(self.query) / 5  # can be changed

        if min_edit_dist <= min_edit_dist_threshold:
            self.query = titleLong_col[min_edit_dist_index]
        


    def get_similarity_array(self, tf_idf_vectorizer, all_docs_tfidf, data):
        """Gets the similarity array.
        
        How similar the doc is to the query is determined by the cosine similarity 
        score.
        """
        self.put_space_in_subj_catNbr_query(data)

        self.misspelling_edit_distance(data)

        query_tfidf = tf_idf_vectorizer.transform([self.query])
        sim_array = cosine_similarity(query_tfidf, all_docs_tfidf).flatten()
        
        
        sim_array = self.check_query_if_subj_course_num(sim_array, data)

        return sim_array
    
    
    def get_ranked_course_indices(self, tf_idf_vectorizer, all_docs_tfidf, data):
        """Gets the list of indices of the ranked courses.
        """

        sim_array = self.get_similarity_array(tf_idf_vectorizer, all_docs_tfidf, data)
        sorted_indices_all = list(np.argsort(sim_array)[::-1])
        sorted_sim_array = sorted(sim_array)[::-1]  # descending order
        
        # only keep the indices of the courses with which the query has the
        # specified cosine similarity score or higher
        cos_sim_score = 0.05  # can be changed
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

    # the subject, catalogNbr, titleLong, and description put together
    subj_nbr_title_desc_series = subject_col + " " + catalogNbr_col + " " + titleLong_col + " " + description_col

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


def main():
    query = "language and information"
    RankedCoursesObj = RankedCourses(query)
    course_contents = get_course_data()
    normalized_data = pd.json_normalize(course_contents)
    tf_idf_vectorizer, docs_tf = get_tfidf_matrix(normalized_data)
    ranked_course_indices = RankedCoursesObj.get_ranked_course_indices(tf_idf_vectorizer,docs_tf, normalized_data)
    print(ranked_course_indices)

if __name__ == "__main__":
    main()
    

