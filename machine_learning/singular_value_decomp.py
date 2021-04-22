import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse.linalg import svds
import matplotlib
import matplotlib.pyplot as plt
from sklearn.preprocessing import normalize

def find_similar_course(doc_term_TF_matrix=None, terms=None, vectorizer=None, desc_example=None,documents=None):
    #From a title and description of course retrieve similar courses
    #Methodology: Perform SVD on ratemyproffesor data and course_desc
    #Identify the particular course, that you want to find similar ones for.
    #Use nearest neighbor to find 10 most similar courses
    if isinstance(doc_term_TF_matrix,None):
        vectorizer = TfidfVectorizer(stop_words='english', max_df=.8,min_df=2)
        doc_term_TF_matrix = vectorizer.fit_transform([x[2] for x in documents]).transpose()

    SVM_decomp(doc_term_TF_matrix,vectorizer)
    #SVM with feedforward selection?
    #Use all features RMP
    #Use all features Course_desc
    #Use subset RMP
    #Use subset Course_desc
    #Use combination of features from RMP and Course_dat


    #WHAT IF RMP does not exists? -> Course desc

def SVM_decomp(matrix,vectorizer):
    u, s, v_trans = svds(matrix, k=100)
    print(u.shape)
    print(s.shape)
    print(v_trans.shape)

    plt.plot(s[::-1])
    plt.xlabel("Singular value number")
    plt.ylabel("Singular value")
    plt.show()

    #Based on plot choose how many dim, we need
    new_k = 40
    words_compressed, _, docs_compressed = svds(matrix, k=new_k)
    docs_compressed = docs_compressed.transpose()

    print(words_compressed.shape)
    print(docs_compressed.shape)

    word_to_index = vectorizer.vocabulary_
    index_to_word = {i: t for t, i in word_to_index.iteritems()}
    print(words_compressed.shape)

    #Magic time
    word_to_index = vectorizer.vocabulary_
    index_to_word = {i:t for t,i in word_to_index.iteritems()}
    print(words_compressed.shape)

    words_compressed = normalize(words_compressed, axis=1)
    closest_words("nuclear",word_to_index,words_compressed,index_to_word)


def closest_words(word_in, word_to_index,words_compressed,index_to_word,k = 10):
    if word_in not in word_to_index: return "Not in vocab."
    sims = words_compressed.dot(words_compressed[word_to_index[word_in],:])
    asort = np.argsort(-sims)[:k+1]
    return [(index_to_word[i],sims[i]/sims[asort[0]]) for i in asort[1:]]

