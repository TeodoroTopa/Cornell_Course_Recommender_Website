from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "Cornell Course Recommender"
net_id = "Joanna Saikali (js3548), Yanchen Zhan (yz366), Mads Christian Berggrein Andersen (mba93), Teodoro Topa (tst42), Marina Cheng (mkc236)"

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
words_compressed = None

class_levels = ['undergrad', 'graduate']
grading_scheme = ['sat-unsat', 'letter-grade']
credits = ['all-credits', 'one-credit', 'two-credit', 'three-credit', 'four-credit', 'five-plus-credit']
locations = ['ithaca-campus', 'cornell-tech', 'other-location']
input_to_data = {
	"undergrad":(["acadCareer"],["UG"]),
	"graduate":(["acadCareer"],["GR","LA","VM","GM"]),
	"sat-unsat":(["gradingBasis"],["OPT","OPI","SUI","SUS"]),
	"letter-grade":(["gradingBasis"],["OPT","OPI","GRI","GRD"]),
	"one-credit":(["unitsMinimum", "unitsMaximum"],[1,1]),
	"two-credit":(["unitsMinimum", "unitsMaximum"],[2,2]),
	"three-credit":(["unitsMinimum", "unitsMaximum"],[3,3]),
	"four-credit":(["unitsMinimum", "unitsMaximum"],[4,4]),
	"five-plus-credit":(["unitsMinimum", "unitsMaximum"],[5,100]),
	"ithaca-campus":(["locationDescr"], ["Ithaca, NY (Main Campus)"]),
	"cornell-tech":(["locationDescr"], ["Cornell Tech"]),
	"other-location":(["locationDescr"], ["Geneva, NY", "AAP in NYC", "Beijing, China", 
		"Engineering in NYC", "Human Ecology in NYC", "Other Domestic", "Other International", 
		"Rome, Italy", "Washington, DC"])
}

if len(course_contents) == 0:
	print("Retrieving course contents from s3...")
	course_contents = get_course_data()
	for course in course_contents:
		ourId_to_course[course['ourId']] = course

if doc_term_tfidf_matrix is None:
	print("Computing TF-IDF...")
	normalized_data = pd.json_normalize(course_contents)
	vectorizer, doc_term_tfidf_matrix = ranked_courses.get_tfidf_matrix(normalized_data)

if words_compressed is None:
	words_compressed = get_svm_data("words_compressed.pkl")
	docs_compressed = get_svm_data("docs_compressed.pkl")

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

def get_saved_classes(email):
	conn = psycopg2.connect(dbname=DB_NAME, port=DB_PORT, user=DB_USER, password=DB_PASS, host=DB_HOST)
	conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
	cur = conn.cursor()
	result = []

	if (email != ""):
		sql = "SELECT * FROM saved_classes WHERE email=\'" + email + "\';"
		cur.execute(sql)
		result = cur.fetchall()
		conn.commit()
	
	cur.close()
	conn.close()

	ret = []
	print (result)
	for (x,y) in result:
		ret.append(y)
	return ret

def filter_on_indices(rankings, filters):
	# if a filter is None, then go through the rankings to remove courses
	# that meet the criteria of which the filter was not initially set
	# ...
	# return a new list of rankings

	global input_to_data

	ret = rankings

	# create a list of classes that we want to filter out of our rankings
	remove_these_classes = []
	for i in range(0,len(filters)):
		for (category,applied) in filters[i]:
			if (applied == None):
				remove_these_classes.append(category)
	if ("all-credits" in remove_these_classes):
		remove_these_classes.remove("all-credits")
	print (remove_these_classes)

	# begin to filter out classes from rankings
	for filter_out in remove_these_classes:
		corresponding_tuple = input_to_data[filter_out]
		filter_by_category = corresponding_tuple[0]
		filter_by_specifics = corresponding_tuple[1]

		test = True

		idx = 0
		# look through rankings to determine which classes should be removed
		while (idx < len(ret)):
			index = ret[idx]
			course = course_contents[index]
			if (len(filter_by_category) == 1):
				val_to_comp = course[filter_by_category[0]]
				if (val_to_comp in filter_by_specifics):
					if (test):
						print ("REMOVING!!!!!! " + filter_by_category[0] + "\t" + val_to_comp)
						print (course['titleLong'])
						test = False
					del ret[idx]
					idx -= 1
			else: # remove class based on credit ranges
				min_credits = filter_by_specifics[0]
				max_credits = filter_by_specifics[1]
				min_to_comp = course[filter_by_category[0]]
				max_to_comp = course[filter_by_category[1]]
				if (not (min_to_comp >= min_credits and max_to_comp <= max_credits)): # check this logic
					del ret[idx]
					idx -= 1
			idx += 1

	return ret

# function that removes cross-listings from rankings, and
# goes through to check if user has saved a course
def remove_cross_listings(rankings):

	user_saved_classes = get_saved_classes(get_user_email())

	# dictionary of classes to return
	each_course_info = []

	# set of class titles that are in [each_course_info]
	ourId_to_titleLong = dict()
	
	for index in rankings:
		course_name = course_contents[index]['titleLong']
		course_ourId = course_contents[index]['ourId']

		print(course_contents[index]['acadCareer'])

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
			some_course = course_contents[index]
			
			if (user_saved_classes != []):
				if (some_course['ourId'] in user_saved_classes):
					some_course['saved'] = True
				else:
					some_course['saved'] = False
			else:
				some_course['saved'] = False	
			
			if (course_name == "Language and Information"):
				if (not "(Sponsored by the course staff :P) " in some_course['description']):
					some_course['description'] = "(Sponsored by the course staff :P) " + some_course['description']
				each_course_info.insert(0,some_course)
			else:
				each_course_info.append(some_course)
			ourId_to_titleLong[course_ourId] = course_name

		if (len(each_course_info) == 15):
			break

	return each_course_info


def run_info_retrieval(query, filters):
	''' To be replaced with actual query results

	Should return a list of course dictionaries
		Ex: [{"title":"Info Systems", "description": "fun"}, {"title":"Other Course", "description":"less fun"}
	'''
	RankedCoursesObj = RankedCourses(query)
	ranked_courses_indeces = RankedCoursesObj.get_ranked_course_indeces(vectorizer, doc_term_tfidf_matrix)
	filtered_indices = filter_on_indices(ranked_courses_indeces, filters)
	return remove_cross_listings(filtered_indices)


@irsystem.route('/report/', methods=['GET', 'POST'])
def report_error():
	# This function will be called when users want to report
	# an error in the RateMyProfessor link

	# we expect to bring in data that includes course being reported and the
		# new RMP link to replace it
	# CAN DO THIS EASILY BY LINKING TO A FLASK FORM
	
	# we need to find this course's [ourId] and any other course w/ same [ourId]

	# we need to take the new RMP link and replace the current link (JOANNA),
		# reuploading the data to S3 with the updated information / reloading
		# in order for information to be accurate on both servers
	
	return None


@irsystem.route('/similar/', methods=['GET','POST'])
def get_similar():
	if request.args.get('search'):
		return redirect(url_for('irsystem.index', search=request.args.get('search')))
	# print("length:",len(course_contents))
	# vectorizerML, new_course_data = get_terms_and_TFs(pd.DataFrame(course_contents), max_dfq=.3, returntf=False)
	# _, doc_term_TF_matrix, vectorizerML, _ = get_terms_and_TFs(pd.DataFrame(course_contents), max_dfq=.5)
	_, _, vectorizerML, _ = get_terms_and_TFs(pd.DataFrame(course_contents), max_dfq=.5)

	# words_compressed, s, docs_compressed = SVM_decomp(dimensions=100, matrix=doc_term_TF_matrix,vectorizer=vectorizerML)
	# pickle.dump(words_compressed, open("words_compressed.pkl", "wb"))
	# pickle.dump(docs_compressed, open("docs_compressed.pkl", "wb"))

	# print("WORDS SIZE: "+ str(sys.getsizeof(words_compressed)))
	# print("DOCS SIZE: "+ str(sys.getsizeof(docs_compressed)))
	# print("vectorizerML SIZE: "+ str(sys.getsizeof(vectorizerML)))
	# print("new_course_data SIZE: "+ str(sys.getsizeof(new_course_data)))

	classNbr = request.args.get('classNbr')
	# print("COURSE ID: " + str(classNbr))
	course_classNbrs = [c['classNbr'] for c in course_contents if c['description'] != None]
	mapping_to_new_idx = [idx for idx,c in enumerate(course_contents) if c['description'] != None]


	course = [c for c in course_contents if c['classNbr']==int(classNbr)]
	course_classNbr = course[0]['classNbr']
	svm_idx = np.where(course_classNbr==np.array(course_classNbrs))[0][0]
	# print("svd index: ",svm_idx)
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
		# print("sim_course_idx: ",sim_course_idx,sim_course_idx.shape)
		# print(course_data.iloc[sim_course_idx][["titleLong"]])
		# print(course_contents[sim_course_idx]["titleLong"],type(course_contents[sim_course_idx]["titleLong"]),len(course_contents[sim_course_idx]["titleLong"]))
		new_sim_idx = mapping_to_new_idx[sim_course_idx]
		title = course_contents[new_sim_idx]["titleLong"]
		# print("Test :: : : ,",title)
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

	'''
	HERE - for each line in results, add a dictionary entry on whether
	some user has saved the class or not
	'''
	user_saved_classes = get_saved_classes(get_user_email())
	if (user_saved_classes != []):
		for some_course in results:
			if (some_course['ourId'] in user_saved_classes):
				some_course['saved'] = True
			else:
				some_course['saved'] = False

	#
	# ordering = dict(zip(course_ids,range(len(course_ids))))
	# results = [("should be c",ordering[c['crseId']],c['titleLong']) for c in course_contents if c['crseId'] in course_ids]
	# results = sorted(results)
	# print(results)
	# print(results,type(results))

	return render_template('similar.html', name=project_name, netid=net_id,
						   output_message="", data=results, query="", crse=course[0],
						   is_logged=google_auth.is_logged_in(), username=get_user_info())


def get_filters():
	global class_levels
	class_levels_response = []; class_level_boolean = True
	for level in class_levels:
		res = request.args.get(level)
		class_levels_response.append((level, res))
		if (res != None):
			class_level_boolean = False
	if (class_level_boolean):
		for i in range(0,len(class_levels_response)):
			class_levels_response[i]=(class_levels_response[i][0],'on')
	print (class_levels_response)

	global grading_scheme
	grading_scheme_response = []; grading_scheme_boolean = True
	for scheme in grading_scheme:
		res = request.args.get(scheme)
		grading_scheme_response.append((scheme, res))
		if (res != None):
			grading_scheme_boolean = False
	if (grading_scheme_boolean):
		for i in range(0,len(grading_scheme_response)):
			grading_scheme_response[i]=(grading_scheme_response[i][0],'on')
	print (grading_scheme_response)

	global credits
	credits_response = []; credits_boolean = True
	for num in credits:
		res = request.args.get(num)
		credits_response.append((num, res))
		if (res != None):
			credits_boolean = False
	if (credits_boolean):
		for i in range(0,len(credits_response)):
			credits_response[i]=(credits_response[i][0],'on')
	print (credits_response)

	global locations
	location_response = []; locations_boolean = True
	for location in locations:
		res = request.args.get(location)
		location_response.append((location, res))
		if (res != None):
			locations_boolean = False
	if (locations_boolean):
		for i in range(0,len(location_response)):
			location_response[i]=(location_response[i][0],'on')
	print (location_response)

	return [class_levels_response, grading_scheme_response, credits_response, location_response]
	

@irsystem.route('/', methods=['GET'])
def index():
	query = request.args.get('search')
	if not query:
		return render_template('index.html', name=project_name, netid=net_id,
							   is_logged=google_auth.is_logged_in(), username=get_user_info())
	else:
		user_filters = get_filters()
		data = run_info_retrieval(query, user_filters)
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
			return render_template('saved.html', is_logged=True, username=google_auth.get_user_info()['given_name'])
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

	else: # make the change in here to remove a class too
		ourId = request.args.get('ourId')
		email = get_user_email()

		# add this class's ourId to database, along with user's name
		conn = psycopg2.connect(dbname=DB_NAME, port=DB_PORT, user=DB_USER, password=DB_PASS, host=DB_HOST)
		conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
		cur = conn.cursor()
		
		sql = "SELECT * FROM saved_classes WHERE email=\'" + email + "\' AND ourId=\'" + ourId + "\';"
		cur.execute(sql)
		result = cur.fetchall()
		print (result)
		conn.commit()

		if (result == []):
			sql = "INSERT INTO saved_classes VALUES (\'" + email + "\', " + ourId + ");"
			print (sql)
			cur.execute(sql)
			conn.commit()
		
		else:
			sql = "DELETE FROM saved_classes WHERE email=\'" + email + "\' AND ourId=\'" + ourId + "\';"
			print (sql)
			cur.execute(sql)
			conn.commit()
		
		cur.close()
		conn.close()

		return redirect(request.referrer)
