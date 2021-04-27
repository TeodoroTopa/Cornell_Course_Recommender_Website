import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse.linalg import svds
import matplotlib
import matplotlib.pyplot as plt
from sklearn.preprocessing import normalize
from sklearn.neighbors import NearestNeighbors
import pickle,os

def save_SVM_pickle(words_compressed,s,docs_compressed ):
    data_SVM = [words_compressed,s,docs_compressed]
    SVM = "SVM_pickle_2021SP.dat"
    with open(SVM, "wb") as f:
        pickle.dump(len(data_SVM), f)
        for value in data_SVM:
            pickle.dump(value, f)


def find_similar_course(vectorizer=None, desc_example=None, docs_compressed=None, words_compressed=None):
    #From a title and description of course retrieve similar courses
    #Methodology: Perform SVD on ratemyproffesor data and course_desc
    #Identify the particular course, that you want to find similar ones for.
    #Use nearest neighbor to find 10 most similar courses
    # if isinstance(type(doc_term_TF_matrix),None):
    #     vectorizer = TfidfVectorizer(stop_words='english', max_df=.8,min_df=2)
    #     doc_term_TF_matrix = vectorizer.fit_transform([x[2] for x in documents]).transpose()


    neigh = NearestNeighbors(n_neighbors=20)
    neigh.fit(docs_compressed.T)

    vec_desc = vectorizer.transform(desc_example)
    print("SHAPES. vec_desc:{} words_compressed {}".format(vec_desc.shape,words_compressed.shape))
    svm_vec_desc = vec_desc @ words_compressed.T

    results = neigh.kneighbors(svm_vec_desc, return_distance=False)
    print("result shape",results.shape)
    return results.squeeze()
    #SVM with feedforward selection?
    #Use all features RMP
    #Use all features Course_desc
    #Use subset RMP
    #Use subset Course_desc
    #Use combination of features from RMP and Course_dat


    #WHAT IF RMP does not exists? -> Course desc

def SVM_decomp(dimensions = 100,matrix=None,vectorizer=None):
    """ matrix is doc_term_TF_matrix"""
    # u, s, v_trans = svds(matrix.astype(float), k=100)
    # print(u.shape)
    # print(s.shape)
    # print(v_trans.shape)

    # plt.plot(s[::-1])
    # plt.xlabel("Singular value number")
    # plt.ylabel("Singular value")
    # plt.show()

    #Based on plot choose how many dim, we need

    # new_k = 100
    docs_compressed, s, words_compressed = svds(matrix.astype(float), k=dimensions)
    docs_compressed = docs_compressed.transpose()
    return words_compressed,s,docs_compressed
#     print(words_compressed.shape)
#     print(docs_compressed.shape)
#
#     word_to_index = vectorizer.vocabulary_
#     index_to_word = {i: t for t, i in word_to_index.items()}
#     print(words_compressed.shape)
#
#     words_compressed = normalize(words_compressed, axis=1)
#     closest_words("nuclear",word_to_index,words_compressed,index_to_word)
#
#
# def closest_words(word_in, word_to_index,words_compressed,index_to_word,k = 10):
#     if word_in not in word_to_index: return "Not in vocab."
#     sims = words_compressed.dot(words_compressed[word_to_index[word_in],:])
#     asort = np.argsort(-sims)[:k+1]
#     return [(index_to_word[i],sims[i]/sims[asort[0]]) for i in asort[1:]]
#

def suprise_me_based_on_liked_courses(saved_course_list):
    """
    SVM could also allow for a “Surprise me”-button within a faculty. User selects a subset of already taken courses that the user likes, and
     our application will convert these courses into the SVM feature representation and find the course with the smallest distance to all of the
      liked courses.
    """
