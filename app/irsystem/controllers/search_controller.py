from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "Cornell Course Recommender"
net_id = "Marina Cheng (mkc236), Joanna Saikali (js3548), Yanchen Zhan (yz366), Mads Christian Berggrein Andersen (mba93), Teodoro Topa (tst42)"

from app.irsystem.models.ranked_courses import RankedCourses
from app.irsystem.models import ranked_courses
import pandas as pd
from data_summary.course_data_summary import get_terms_and_TFs
from machine_learning.singular_value_decomp import find_similar_course, SVM_decomp
import pickle
import sys

from app.accounts.controllers import google_auth

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy.engine.url import make_url
''' connect to database '''
''' note that these credentials may need to change '''
DATABASE_URL = os.environ['DATABASE_URL']
url = make_url(DATABASE_URL)
DB_NAME = url.database
DB_PORT = url.port
DB_USER = url.username
DB_PASS = url.password
DB_HOST = url.host

course_contents = []
ourId_to_course = dict()
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
	for course in course_contents:
		ourId_to_course[course['ourId']] = course

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

def get_user_email():
	if google_auth.is_logged_in():
		user_info = google_auth.get_user_info()
		email = user_info["email"]
		return email
	else:
		return ""

@irsystem.route('/similar/', methods=['GET','POST'])
def get_similar():
	if request.args.get('search'):
		return redirect(url_for('irsystem.index', search=request.args.get('search')))
	print("length:",len(course_contents))
	# vectorizerML, new_course_data = get_terms_and_TFs(pd.DataFrame(course_contents), max_dfq=.3, returntf=False)
	_, doc_term_TF_matrix, vectorizerML, _ = get_terms_and_TFs(pd.DataFrame(course_contents), max_dfq=.5)

	words_compressed, s, docs_compressed = SVM_decomp(dimensions=100, matrix=doc_term_TF_matrix,vectorizer=vectorizerML)
	pickle.dump(words_compressed, open("words_compressed.pkl", "wb"))
	pickle.dump(docs_compressed, open("docs_compressed.pkl", "wb"))

	# words_compressed = get_svm_data("words_compressed.pkl")
	# docs_compressed = get_svm_data("docs_compressed.pkl")
	# print("WORDS SIZE: "+ str(sys.getsizeof(words_compressed)))
	# print("DOCS SIZE: "+ str(sys.getsizeof(docs_compressed)))
	# print("vectorizerML SIZE: "+ str(sys.getsizeof(vectorizerML)))
	# print("new_course_data SIZE: "+ str(sys.getsizeof(new_course_data)))

	classNbr = request.args.get('classNbr')
	print("COURSE ID: " + str(classNbr))
	course_classNbrs = [c['classNbr'] for c in course_contents if c['description'] != None]
	mapping_to_new_idx = [idx for idx,c in enumerate(course_contents) if c['description'] != None]


	course = [c for c in course_contents if c['classNbr']==int(classNbr)]
	course_classNbr = course[0]['classNbr']
	svm_idx = np.where(course_classNbr==np.array(course_classNbrs))[0][0]
	print("svd index: ",svm_idx)
	# print(type(course),course_contents[1])
	# print("NAME: " + str(course[0]['titleLong']))
	# course_data = pd.DataFrame(course_contents)
	# print("Course: ",course[0].keys())
	# print(course[0]['crseId'])
	# print(course)
	# course_desc = course[0]['description']
	# print("Columns: ",course_data.columns,"\n")
	# print(np.count_nonzero(course_data['crseId'] == int(courseid)),course_data['crseId'] == int(courseid))
	# idx = np.where(course_data['classNbr'] == int(classNbr))[0][0]
	# print("TEST IDX",idx)
	# desc = "" if course[0]['description'] is None else course[0]['description']
	# course_desc = pd.DataFrame({"description":[" " +desc]})["description"]

	#course_desc = course[0]['titleLong'] + " " + course_data[course_data['classNbr'] == int(classNbr)]['description']
	# print(course_desc)

	# course_desc = course[0]['description']
	# print(course_data.head())

	###  ML ####
	similar_courses = find_similar_course(svm_idx, docs_compressed, words_compressed)
	titles = [course[0]['titleLong']]
	classNbrs = []
	for sim_course_idx in similar_courses:
		print("sim_course_idx: ",sim_course_idx,sim_course_idx.shape)
		# print(course_data.iloc[sim_course_idx][["titleLong"]])
		# print(course_contents[sim_course_idx]["titleLong"],type(course_contents[sim_course_idx]["titleLong"]),len(course_contents[sim_course_idx]["titleLong"]))
		new_sim_idx = mapping_to_new_idx[sim_course_idx]
		title = course_contents[new_sim_idx]["titleLong"]
		print("Test :: : : ,",title)
		if title not in titles:
			classNbrs.append( int(course_contents[new_sim_idx]["classNbr"]))
			titles.append(title)
		# print("course_id",classNbrs[-1])
	# print(similar_courses,type(course_contents),len(course_contents),type(course_contents[0]))
	# results = [c for c in course_contents if c['classNbr'] in classNbrs]
	# results = [course_contents[course_contents['classNbr'] == classNbr] for classNbr in classNbrs]
	# results = [course_data[course_data['crseId'] == int(course_id)] for course_id in course_ids]

	ordering = dict(zip(classNbrs,range(len(classNbrs))))
	results = []
	alphas = ['a','b',"t","p","r","d","c","i","o","k","x","l","j"]
	count = 0
	for c in course_contents:
		if c['classNbr'] in classNbrs:
			# results.append(c)
			results.append((c,ordering[c['classNbr']]))
			count +=1
			classNbrs.remove(c['classNbr'])
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
		
		email = get_user_email()

		conn = psycopg2.connect(dbname=DB_NAME, port=DB_PORT, user=DB_USER, password=DB_PASS, host=DB_HOST)
		conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
		cur = conn.cursor()

		sql = "SELECT ourId FROM saved_classes WHERE email=\'" + email + "\';"
		cur.execute(sql)
		result = cur.fetchall()
		print (result)

		conn.commit()

		cur.close()
		conn.close()

		if (result == []):
			print ("empty")
			return render_template('saved.html')
		else:
			# extract data of classes saved, loaded into [data]
			data = []

			for (saved_ourId,) in result:
				data.append(ourId_to_course[saved_ourId])

			return render_template('saved.html', is_logged=True, data=data, username=google_auth.get_user_info()['given_name'])
	
	else:
		return redirect(url_for('accounts.login'))


@irsystem.route('/save_course', methods=['GET'])
def save_course():
	if not (google_auth.is_logged_in()):
		return redirect(url_for('accounts.login'))

	else:
		ourId = request.args.get('ourId')
		email = get_user_email()

		# add this class's ourId to database, along with user's name
		conn = psycopg2.connect(dbname=DB_NAME, port=DB_PORT, user=DB_USER, password=DB_PASS, host=DB_HOST)
		conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
		cur = conn.cursor()
		
		sql = "INSERT INTO saved_classes VALUES (\'" + email + "\', " + ourId + ");"
		print (sql)
		cur.execute(sql)
		conn.commit()
		
		cur.close()
		conn.close()

		# return back to initial line, passing through a "saved" parameter to 
		# determine if a course should be unsaved

		# need to return template back to initial state, with link changed to "unsave"
		return render_template('search.html')
