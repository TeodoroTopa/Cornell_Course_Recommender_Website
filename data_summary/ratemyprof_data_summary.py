"""
Summary of the RateMyProfessor data.
The input is the rate_my_professor.json file of RateMyProfessor data.

"""
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt
from scipy.stats import describe


def get_data():
    """Gets the data.
    """

    filename = "rate_my_professor.json"
    data = pd.read_json(filename)

    return data


def get_professor_summary(data):
    """Professor summary.
    """

    professor_col = data.loc[:,'prof_name']
    num_professors = len(professor_col.unique())  # number of different professors
    print("Number of different professors:", num_professors)


def get_department_summary(data):
    """Department summary.
    """

    department_col = data.loc[:,'prof_dept']
    num_departments = len(department_col.unique())  # number of different departments
    print("Number of different departments:", num_departments)


def get_class_name_summary(data):
    """Class name summary.
    """

    class_name_col = data.loc[:,'class_name']
    
    # Counting the number of "class names" (including duplicate class names) 
    # that only have the number or department in it because the "class names" 
    # are in a [departmentabbrev][classnumber] format and if the name does not 
    # follow the format, the same class might be counted more than once.
    class_names_with_both_alpha_and_num = []
    for class_name in class_name_col:
        # include only if the class name contains both digits and letters
        if not (class_name.isalpha() or class_name.isdigit()):
            class_names_with_both_alpha_and_num.append(class_name)
    
    unique_classes = set(class_names_with_both_alpha_and_num)
    num_classes = len(unique_classes)  # number of different classes
    print("Number of different classes (with both letters and numbers in their name):", num_classes)


def get_attendance_mandatory_summary(data):
    """Attendance summary. Whether attendance was manditory or not.
    """
    
    attendance_col = data.loc[:,'attendance_mandatory']  # column of 0/1 inputs (if present)

    attendance_unique_vals = attendance_col.unique()
    print("The unique values of the attendance column:", attendance_unique_vals)

    num_no_responses = sum(attendance_col.isna())  # number of no responses
    num_1s = sum(attendance_col[attendance_col == 1.0])
    num_0s = len(attendance_col) - num_no_responses - num_1s

    print("For attendance mandatory, number of no responses:", num_no_responses)
    print("Number of ratings that say attendance is mandatory:", num_1s)
    print("Number of ratings that say attendance is not mandatory:", num_0s)
    


def get_credit_summary(data):
    """Credit summary.
    """
    
    credit_col = data.loc[:,'credit']  # column of TRUE/FALSE statements
    
    # number of rows that have "TRUE" in the `credit` column
    num_credit_true = np.sum(credit_col[credit_col == True])
    
    num_credit_false = 'NA'  # to print 'NA' if there are empty rows in the `credit` column
    # number of rows that have "FALSE" in the "credit" column
    if np.sum(credit_col.isna()) == 0:  # checking that there is a value in each row of the `credit` column
        num_credit_false = len(credit_col) - num_credit_true

    print("Number of 'TRUE' values in the 'credit' column:")
    print(num_credit_true)
    print("Number of 'FALSE' values in the 'credit' column:")
    print(num_credit_false)


def get_difficulty_summary(data):
    """Difficulty summary. How difficult the course is (range 1 to 5).
    """
    
    difficulty_col = data.loc[:,'difficulty']
    difficulty_summary_stats = describe(difficulty_col)
    print("Summary statistics of difficulty levels (1-5) of courses:")
    print(difficulty_summary_stats)


def get_grade_summary(data):
    """Grade summary. What grade the rater received in the class.
    """
    
    grade_col = data.loc[:,'grade']
    unique_grades = grade_col.unique()

    print("The different grade inputs:", unique_grades)


def get_take_again_summary(data):
    """Take again summary. Whether the rater would take the class again or not.
    """
    
    take_again_col = data.loc[:,'take_again']  # column of 0/1 inputs (if present)

    take_again_unique_vals = take_again_col.unique()
    print("The unique values of the 'take_again' column:", take_again_unique_vals)

    num_no_responses = sum(take_again_col.isna())
    num_1s = sum(take_again_col[take_again_col == 1.0])
    num_0s = len(take_again_col) - num_no_responses - num_1s

    print("For take again, number of no responses:", num_no_responses)
    print("Number of ratings that say would take again:", num_1s)
    print("Number of ratings that say would not take again:", num_0s)


def get_comment_summary(data):
    """Comment summary. Comments about the professor and class.
    """
    
    comment_col = data.loc[:, 'comment']
    num_wo_comments = np.sum(comment_col.isna())  # number of ratings without comments
    num_rows = len(comment_col)
    num_w_comments = num_rows - num_wo_comments  # number of ratings with comments

    print("Number of ratings with comments:", num_w_comments)
    print("Number of ratings without comments:", num_wo_comments)


def get_terms_and_TFs(data):
    """Gets the terms and TFs of the terms from the "comment" column.

    Stop words are not used.
    """

    comment_col = data.loc[:,'comment']

    # dropping comments that correspond to ratings that don't have comments
    # (if NA values exist)
    comment_col = comment_col.dropna()

    vectorizer = CountVectorizer(stop_words='english')  # don't use stop words

    doc_term_TF_matrix = vectorizer.fit_transform(comment_col).toarray()
    term_doc_TF_matrix = doc_term_TF_matrix.T

    # getting an array of the number of documents each term is in,
    # where each element corresponds to a term
    terms_TF = np.sum(term_doc_TF_matrix, axis=1)  # the TF of the terms

    terms = vectorizer.get_feature_names()  # the terms

    num_terms = len(terms)
    print("Number of terms among comments:", num_terms)

    num_terms_mult_occ = len(terms_TF) - sum(terms_TF == 1)
    print("Number of terms that occur more than once:", num_terms_mult_occ)

    return (terms, terms_TF)


def produce_plot(data, terms, terms_TF):
    """Produces the plot of the RateMyProfessor rating comment term frequencies of the top terms.
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
    plt.title("RateMyProfessor Rating Comment Term Frequencies of the Top " + str(num_top_terms) + " Terms")
    plt.show()


def main():
    data = get_data()
    get_professor_summary(data)
    get_department_summary(data)
    get_class_name_summary(data)
    get_attendance_mandatory_summary(data)
    get_credit_summary(data)
    get_difficulty_summary(data)
    get_grade_summary(data)
    get_take_again_summary(data)
    get_comment_summary(data)
    (terms, terms_TF) = get_terms_and_TFs(data)
    produce_plot(data, terms, terms_TF)


if __name__ == "__main__":
    main()

