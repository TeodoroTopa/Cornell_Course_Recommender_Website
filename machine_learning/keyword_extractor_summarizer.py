import json,pandas as pd, numpy as np, matplotlib.pyplot as plt,os
from data_summary.course_data_summary import get_data,get_terms_and_TFs
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize, sent_tokenize

def keyword_extractor(doc_term_TF_matrix,terms,vectorizer,description,n=10):
    """
    Example on how to use:

    course_data, course_desc = load_course_descriptions()
    terms, terms_TF,doc_term_TF_matrix,vectorizer  = get_terms_and_TFs(course_data,max_dfq=.5)
    for i in range(1,3000,1000):
        print(course_data.iloc[i][["titleLong"]])
        desc_example = course_desc.iloc[i]
        a = vectorizer.transform(desc_example)
        keyword_extractor(doc_term_TF_matrix,terms,vectorizer,desc_example,n=3)
        print("#####")

    The function get_terms_and_TFs() is from in data_summary.course_data_summary
    The function load_course_descriptions() is from machine_learning.main_ml
    """



    tfidf_transformer = TfidfTransformer(smooth_idf=True, use_idf=True)
    tfidf_transformer.fit(doc_term_TF_matrix)
    if isinstance(description,pd.core.series.Series):
        description= vectorizer.transform(description)

    tf_idf_desc = tfidf_transformer.transform(description)
    items = tf_idf_desc.tocoo()

    tuples = zip(items.col, items.data)
    sorted_items = sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)

    sorted_items = sorted_items[:n]

    score_vals = []
    feature_vals = []

    for idx, score in sorted_items:
        score_vals.append(np.round(score, 4))
        feature_vals.append(terms[idx])


    results = {}
    for idx in range(len(feature_vals)):
        results[feature_vals[idx]] = score_vals[idx]


    for k in results:
        print(k, results[k])
    return results

def text_extractor(course_desc,query,doc_term_TF_matrix,terms,vectorizer):
    """
    Get sentences
    For each sentence find a similarity score
    Find the sentence with largest score. Add that and the next 2-3 sentences.
    """
    query = query.lower()
    query_vec = vectorizer.transform(pd.Series(query))
    sentences = sent_tokenize(course_desc)
    sentences_vec = [vectorizer.transform(pd.Series(sentence)) for sentence in sentences]

    tfidf_transformer = TfidfTransformer(smooth_idf=True, use_idf=True)
    tfidf_transformer.fit(doc_term_TF_matrix)

    tf_idf_desc = tfidf_transformer.transform(query_vec)
    tf_idf_sentences = [tfidf_transformer.transform(sentence) for sentence in sentences_vec]

    sim_array = np.zeros(len(sentences_vec))  # array of similarity scores

    array_1 = tf_idf_desc
    for i in range(len(sentences_vec)):
        array_2 = tf_idf_sentences[i]
        sim_array[i] = cosine_similarity(array_1, array_2)
    print(course_desc)
    print("Most:",sentences[np.argmax(sim_array)])
