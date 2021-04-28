from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "Cornell Course Recommender"
net_id = "Marina Cheng (mkc236), Joanna Saikali (js3548), Yanchen Zhan (yz366), Mads Christian Berggrein Andersen (mba93), Teodoro Topa (tst42)"

from app.irsystem.models.ranked_courses import RankedCourses
from app.irsystem.models import ranked_courses
from app.irsystem.models.elasticsearch_ranked_courses import ElasticsearchRankedCourses
from app.irsystem.models.ranked_courses_db import DB_Access
import pandas as pd
from data_summary.course_data_summary import get_terms_and_TFs
from machine_learning.singular_value_decomp import find_similar_course, SVM_decomp
import pickle
import sys

from app.accounts.controllers import google_auth

course_contents = []
doc_term_tfidf_matrix = None
vectorizer = None
# terms = None
# terms_TF = None
# doc_term_TF_matrix = None
# vectorizerML = None
# new_course_data = None
# words_compressed = None
# docs_compressed = None
if len(course_contents) == 0:
	print("Retrieving course contents from s3...")
	course_contents = get_course_data()
if doc_term_tfidf_matrix is None:
	print("Computing TF-IDF...")
	normalized_data = pd.json_normalize(course_contents)
	vectorizer, doc_term_tfidf_matrix = ranked_courses.get_tfidf_matrix(normalized_data)

def remove_cross_listings(rankings):

	# dictionary of classes to return
	each_course_info = []

	# set of class titles that are in [each_course_info]
	ourId_to_titleLong = dict()
	
	for index in rankings:
		course_name = course_contents[index]['titleLong']
		course_ourId = course_contents[index]['ourId']

		# if the course already exists in [each_course_unique]
		if (course_ourId in ourId_to_titleLong.keys()):

			# index to first course in the set where this [ourId] appears
			list_of_ourIds = []
			for course in each_course_info:
				list_of_ourIds.append(course['ourId'])
			idx = list_of_ourIds.index(course_ourId)

			# then update the description, adding it on to original description
			previous_class = each_course_info[idx]
			cross_list_string = " Cross-listed with " + str(course_contents[index]['subject']) + " " + str(course_contents[index]['catalogNbr'] + ".")
			if (each_course_info[idx]['description'].find(cross_list_string) == -1):
				each_course_info[idx]['description'] = previous_class['description'] + cross_list_string 

		else:
			each_course_info.append(course_contents[index])
			ourId_to_titleLong[course_ourId] = course_name

		if (len(each_course_info) == 15):
			break

	return each_course_info

def run_info_retrieval(query):
	''' To be replaced with actual query results

	Should return a list of course dictionaries
		Ex: [{"title":"Info Systems", "description": "fun"}, {"title":"Other Course", "description":"less fun"}
	'''
	RankedCoursesObj = RankedCourses(query)
	ranked_courses_indeces = RankedCoursesObj.get_ranked_course_indeces(vectorizer, doc_term_tfidf_matrix)
	return remove_cross_listings(ranked_courses_indeces)
	

def get_user_info():
	if google_auth.is_logged_in():
		user_info = google_auth.get_user_info()
		name = user_info['given_name']
		return name
	else:
		return ""

@irsystem.route('/similar/', methods=['GET','POST'])
def get_similar():
	if request.args.get('search'):
		return redirect(url_for('irsystem.index', search=request.args.get('search')))
	vectorizerML, new_course_data = get_terms_and_TFs(pd.DataFrame(course_contents), max_dfq=.3, returntf=False)
	# terms_TF, doc_term_TF_matrix, vectorizerML, new_course_data = get_terms_and_TFs(pd.DataFrame(course_contents), max_dfq=.3)

	# words_compressed, s, docs_compressed = SVM_decomp(dimensions=100, matrix=doc_term_TF_matrix,vectorizer=vectorizerML)
	# pickle.dump(words_compressed, open("words_compressed.pkl", "wb"))
	# pickle.dump(docs_compressed, open("docs_compressed.pkl", "wb"))

	words_compressed = get_svm_data("words_compressed.pkl")
	docs_compressed = get_svm_data("docs_compressed.pkl")
	print("WORDS SIZE: "+ str(sys.getsizeof(words_compressed)))
	print("DOCS SIZE: "+ str(sys.getsizeof(docs_compressed)))
	print("vectorizerML SIZE: "+ str(sys.getsizeof(vectorizerML)))
	print("new_course_data SIZE: "+ str(sys.getsizeof(new_course_data)))

	classNbr = request.args.get('classNbr')
	print("COURSE ID: " + str(classNbr))
	course = [c for c in course_contents if c['classNbr']==int(classNbr)]
	# print(type(course),course_contents[1])
	print("NAME: " + str(course[0]['titleLong']))
	course_data = pd.DataFrame(course_contents)
	# print("Course: ",course[0].keys())
	# print(course[0]['crseId'])
	# print(course)
	# course_desc = course[0]['description']
	# print("Columns: ",course_data.columns,"\n")
	# print(np.count_nonzero(course_data['crseId'] == int(courseid)),course_data['crseId'] == int(courseid))
	# idx = np.where(course_data['classNbr'] == int(classNbr))[0][0]
	# print("TEST IDX",idx)
	desc = "" if course[0]['description'] is None else course[0]['description']
	course_desc = pd.DataFrame({"description":[" " +desc]})["description"]

	#course_desc = course[0]['titleLong'] + " " + course_data[course_data['classNbr'] == int(classNbr)]['description']
	# print(course_desc)

	# course_desc = course[0]['description']
	# print(course_data.head())

	###  ML ####
	similar_courses = find_similar_course(vectorizerML, course_desc, docs_compressed, words_compressed)
	titles = []
	course_ids = []
	for sim_course_idx in similar_courses:
		print("sim_courses:,",similar_courses,similar_courses.shape," and sim_course_idx: ",sim_course_idx,sim_course_idx.shape)
		# print(course_data.iloc[sim_course_idx][["titleLong"]])
		print(new_course_data.iloc[sim_course_idx][["titleLong"]],type(new_course_data.iloc[sim_course_idx][["titleLong"]]),len(new_course_data.iloc[sim_course_idx][["titleLong"]]))
		title = new_course_data.iloc[sim_course_idx][["titleLong"]][0]
		print("Test :: : : ,",title)
		if title not in titles:
			course_ids.append(new_course_data.iloc[sim_course_idx][["crseId"]][0])
			titles.append(title)
	# print(similar_courses,type(course_contents),len(course_contents),type(course_contents[0]))
	# results = [course_contents[course_contents['crseId'] == course_id] for course_id in course_ids]
	# results = [course_data[course_data['crseId'] == int(course_id)] for course_id in course_ids]

	ordering = dict(zip(course_ids,range(len(course_ids))))
	results = []
	alphas = ['a','b',"t","p","r","d","c","i","o","k","x","l","j"]
	count = 0
	for c in course_contents:
		if c['crseId'] in course_ids:
			# results.append(c)
			results.append((c,ordering[c['crseId']]))
			count +=1
			course_ids.remove(c['crseId'])
	# print("Before sort: ",results)
	results = sorted(results, key = lambda x: x[1])
	results = [result[0] for result in results]
	# print("After sort: ",results)

	#
	# ordering = dict(zip(course_ids,range(len(course_ids))))
	# results = [("should be c",ordering[c['crseId']],c['titleLong']) for c in course_contents if c['crseId'] in course_ids]
	# results = sorted(results)
	# print(results)
	# print(results,type(results))

	return render_template('similar.html', name=project_name, netid=net_id,
						   output_message="", data=results, query="", crse=course[0],
						   is_logged=google_auth.is_logged_in(), username=get_user_info())



@irsystem.route('/', methods=['GET'])
def index():
	query = request.args.get('search')
	if not query:
		return render_template('index.html', name=project_name, netid=net_id,
							   is_logged=google_auth.is_logged_in(), username=get_user_info())
	else:
		data = run_info_retrieval(query)
		output_message =  "Your search: " + query
		return render_template('search.html', name=project_name, netid=net_id,
							   output_message=output_message, data=data, query=query,
							   is_logged=google_auth.is_logged_in(), username=get_user_info())

@irsystem.route('/saved', methods=['GET'])
def saved():
	if google_auth.is_logged_in():
		return render_template('saved.html', is_logged=True, username=google_auth.get_user_info()['given_name'])
	else:
		return redirect(url_for('accounts.login'))

@irsystem.route('/save_course', methods=['GET'])
def save_course():
	if not (google_auth.is_logged_in()):
		return redirect(url_for('accounts.login'))
	else:
		classNbr = request.args.get('classNbr')
		

		# beware of the links and how you pass information in
		return render_template('index.html') 
