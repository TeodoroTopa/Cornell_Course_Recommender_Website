"""
Summary of the course data. The input is the course_data file.

mcheng1
Apr 11, 2021
"""
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt


def get_data():
    """Gets the data.
    """

    path = "../preliminary_scraping/with_roster_api/course_data"
    data = pd.read_json(path)
    
    return data


def get_overall_data_summary(data):
    """Overall data summary. 
    """

    #print(data.head())
    data_shape = data.shape  # dimensions of dataset
    print("Dimensions of the dataset:", data_shape)
    print("Columns of the data:", data.columns)


def get_subject_summary(data):
    """Subject summary.
    """

    subject_col = data.loc[:,'subject']
    num_subjects = len(subject_col.unique())  # number of different subjects
    print("Number of different subjects:", num_subjects)


def get_prereq_summary(data):
    """Prereq summary.
    """

    prereq_col = data.loc[:,'catalogPrereqCoreq']
    num_wo_prereqs = np.sum(prereq_col.isna())  # number of classes without prereqs
    num_rows = len(data)
    num_w_prereqs = num_rows - num_wo_prereqs  # number of classes with prereqs
    print("Number of classes with prereqs:", num_w_prereqs)
    print("Number of classes without prereqs:", num_wo_prereqs)


def get_course_description_summary(data):
    """Course description summary.
    """

    description_col = data.loc[:,'description']
    num_wo_desc = np.sum(description_col.isna())  # number of classes without descriptions
    num_rows = len(data)
    num_w_desc = num_rows - num_wo_desc  # number of classes with descriptions
    print("Number of classes with descriptions:", num_w_desc)
    print("Number of classes without descriptions:", num_wo_desc)


def get_terms_and_TFs(data):
    """Gets the terms and the TFs of the terms.

    Stop words are not used.
    """
    description_col = data.loc[:,'description']

    # dropping descriptions that correpond to classes that don't have descriptions
    description_col = description_col.dropna()

    vectorizer = CountVectorizer(stop_words='english')  # don't use stop words
    
    doc_term_TF_matrix = vectorizer.fit_transform(description_col).toarray()
    term_doc_TF_matrix = doc_term_TF_matrix.T

    # getting an array of number of documents each term is in, 
    # where each element corresponds to a term
    terms_TF = np.sum(term_doc_TF_matrix, axis=1)  # the TF of the terms

    terms = vectorizer.get_feature_names()  # the terms
    
    num_terms = len(terms)
    print("Number of terms among descriptions:", num_terms)

    num_terms_mult_occ = len(terms_TF) - sum(terms_TF == 1)
    print("Number of terms that occur more than once:", num_terms_mult_occ)

    return (terms, terms_TF)


def produce_plot(data, terms, terms_TF):
    """Produces the plot of the course description term frequencies of the top terms.
    """
    terms_terms_TF_tuple = list(zip(terms, terms_TF))
    terms_terms_TF_tuple_sorted = sorted(terms_terms_TF_tuple, key=lambda x: -x[1])

    num_top_terms = 50
    # reverse the array so bars are from longest to shortest in the plot
    top_terms_and_term_counts = terms_terms_TF_tuple_sorted[:num_top_terms][::-1]
    top_term_counts = [term_and_count[1] for term_and_count in top_terms_and_term_counts]
    top_terms = [term_and_count[0] for term_and_count in top_terms_and_term_counts]

    # The plot
    plt.rc('ytick', labelsize=5)  # for smaller font size for labels for each bar
    plt.barh(top_terms, top_term_counts)
    plt.xlabel("Term Frequency")
    plt.ylabel("Top Terms")
    plt.title("Course Description Term Frequencies of the Top " + str(num_top_terms) + " Terms")
    plt.show()

    
def main():
    data = get_data()
    get_overall_data_summary(data)
    get_subject_summary(data)
    get_prereq_summary(data)
    get_course_description_summary(data)
    (terms, terms_TF) = get_terms_and_TFs(data)
    produce_plot(data, terms, terms_TF)


if __name__ == "__main__":
    main()
