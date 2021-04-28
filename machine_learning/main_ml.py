import json,pandas as pd, numpy as np, matplotlib.pyplot as plt,os
from data_summary.course_data_summary import get_data,get_terms_and_TFs
from sklearn.feature_extraction.text import TfidfTransformer
from machine_learning.keyword_extractor_summarizer import keyword_extractor,text_extractor
from machine_learning.singular_value_decomp import find_similar_course
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from nltk.tokenize import word_tokenize, sent_tokenize

def loadData():
    path_course = r'C:\Users\Mads-\Documents\Universitet\6. Semester\INFO4300 Language and Information\course_data'
    # path_rmp = r'C:\Users\Mads-\Documents\Universitet\6. Semester\INFO4300 Language and Information\rate_my_professor.csv'
    # rmp_data = get_data(path=path_rmp, filetype="csv")

    path_rmp = r'C:\Users\Mads-\Documents\Universitet\6. Semester\INFO4300 Language and Information\ratemyprof_svm'
    rmp_data = get_data(path=path_rmp)

    course_data = get_data(path=path_course)
    return course_data, rmp_data

def load_course_descriptions():
    course_data, rmp_data = loadData()
    course_desc = course_data[["description"]]
    return course_data,course_desc, rmp_data



if __name__ == "__main__":
    course_data, _, rmp_data = load_course_descriptions()
    terms_TF,doc_term_TF_matrix,vectorizer,new_course_data  = get_terms_and_TFs(course_data,max_dfq=.8)
    # terms_rmp, terms_TF_rmp,doc_term_TF_matrix_rmp,vectorizer_rmp,new_rmp_data  = get_terms_and_TFs(rmp_data,max_dfq=0.9,rmp=True)


    # Examples of keyword extraction:
    # for i in range(1, 3000, 1000):
    #     print(course_data.iloc[i][["titleLong"]])
    #     desc_example = course_desc.iloc[i]
    #     a = vectorizer.transform(desc_example)
    #     keyword_extractor(doc_term_TF_matrix, terms, vectorizer, desc_example, n=5)
    #     print("#####")
    #
    #
    # # Examples of text extraction:
    # queries = ["Culture and influence","Turing Machine","Advanced linguistics", "information retrieval"]
    # for idx,i in enumerate(range(1, 3000, 1000)):
    #     print(course_data.iloc[i][["titleLong"]])
    #     desc_example = course_desc.iloc[i]
    #     a = vectorizer.transform(desc_example)
    #     keyword_extractor(doc_term_TF_matrix,terms,vectorizer,desc_example,n=3)
    #     print("#####")
    #     print("Query: {}".format(queries[idx]))
    #     test_str = desc_example[0]
    #     summarized_text = text_extractor(test_str,queries[idx],doc_term_TF_matrix,terms,vectorizer)

    #Find similar course
    for idx, i in enumerate(range(1, 3000, 600)):
        i = 1189
        # desc_example = course_desc.iloc[1189]
        desc_example = course_data.iloc[i]['description']
        print("Input title: ",course_data.iloc[i][["titleLong"]][0]," . Input description",desc_example)
        similar_courses = find_similar_course(doc_term_TF_matrix, vectorizer, desc_example)
        titles = []
        course_ids = []
        for sim_course_idx in similar_courses:
            # print(course_data.iloc[sim_course_idx][["titleLong"]])
            title = new_course_data.iloc[sim_course_idx][["titleLong"]][0]
            course_ids.append(new_course_data.iloc[sim_course_idx][["crseId"]][0])
            if title not in titles:
                titles.append(title)
                print(len(titles),".",title)
        print(similar_courses)
    # Find similar course with RMP
    # for idx, i in enumerate(range(1, 3000, 1000)):
    #     # desc_example = course_desc.iloc[1189]
    #     desc_example = course_desc.iloc[i]
    #     print(course_data.iloc[i][["titleLong"]],desc_example)
    #     similar_courses = find_similar_course(doc_term_TF_matrix_rmp, terms_rmp, vectorizer_rmp, desc_example)
    #     #3699 1171 2220  162 3681 3548 2234 1935 1881  319
    #     for sim_course_idx in similar_courses:
    #         # print(course_data.iloc[sim_course_idx][["titleLong"]])
    #         print(new_rmp_data.iloc[sim_course_idx][["class_name"]]," : ",)
    #     test =2


