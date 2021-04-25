from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "Cornell Course Recommender"
net_id = "Marina Cheng (mkc236), Joanna Saikali (js3548), Yanchen Zhan (yz366), Mads Christian Berggrein Andersen (mba93), Teodoro Topa (tst42)"

from app.irsystem.models.ranked_courses import RankedCourses
from app.irsystem.models.elasticsearch_ranked_courses import ElasticsearchRankedCourses
from app.irsystem.models.ranked_courses_db import DB_Access
import pandas as pd


from app.accounts.controllers import google_auth

course_contents = []
normalized_data  = None
tf_idf = None
svm_vector = None

if len(course_contents) == 0:
	print("Retrieving course contents from s3...")
	course_contents = get_course_data()
if normalized_data is None:
	print("Normalizing data...")
	normalized_data = pd.json_normalize(course_contents)
if tf_idf is  None:
	print("Computing TF-IDF...")
	tf_idf_vectorizer, docs_tf = get_tfidf_matrix(normalized_data)
if svm_vector is  None:
	print("Reading in SVM Vector...")
	##

def run_info_retrieval(query):
	''' To be replaced with actual query results

	Should return a list of course dictionaries
		Ex: [{"title":"Info Systems", "description": "fun"}, {"title":"Other Course", "description":"less fun"}
	'''
	RankedCoursesObj = RankedCourses(query)
	ranked_courses_indeces = RankedCoursesObj.get_ranked_course_indeces(tf_idf_vectorizer,docs_tf)
	
	# dictionary of classes to return
	each_course_info = []

	# set of class titles that are in [each_course_info]
	class_titles_unique = set()
	
	for index in ranked_courses_indeces:
		course_name = course_contents[index]['titleLong']
		# if the course already exists in [each_course_unique]
		if (course_name in class_titles_unique):

			# find original course in [each_course_info] (generally the last course entered) and
			# update that class's description to account for a cross-listed class
			previous_class = each_course_info[len(each_course_info) - 1]
			cross_list_string = "Cross-listed with " + str(course_contents[index]['subject']) + " " + str(course_contents[index]['catalogNbr'] + ".")
			each_course_info[len(each_course_info)-1]['description'] = previous_class['description'] + cross_list_string 
			# now, integrate this into the course descriptions so people can have multiple cross-references
			# we need to discuss how to approach this as it relates to how we rank our courses

		else:
			each_course_info.append(course_contents[index])
			class_titles_unique.add(course_name)

		if (len(each_course_info) == 15):
			break

	return each_course_info
	# return [course_contents[index] for index in ranked_courses_index]

def get_user_info():
	if google_auth.is_logged_in():
		user_info = google_auth.get_user_info()
		name = user_info['given_name']
		return name
	else:
		return ""

@irsystem.route('/similar/', methods=['GET','POST'])
def get_similar():
	courseid = request.args.get('courseid')
	print("COURSE ID: " + str(courseid))
	course = [c for c in course_contents if c['crseId']==int(courseid)]
	print("NAME: " + str(course[0]['titleLong']))
	results = course_contents[:10]



	return render_template('search.html', name=project_name, netid=net_id,
						   output_message="", data=results, query="",
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
