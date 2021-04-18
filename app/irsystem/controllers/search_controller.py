from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "Cornell Course Recommender"
net_id = "Marina Cheng (mkc236), Joanna Saikali (js3548), Yanchen Zhan (yz366), Mads Christian Berggrein Andersen (mba93), Teodoro Topa (tst42)"

import boto3
import botocore
from botocore import UNSIGNED
from botocore.config import Config
from app.irsystem.models.ranked_courses import RankedCourses
from app.irsystem.models.elasticsearch_ranked_courses import ElasticsearchRankedCourses


def run_info_retrieval(query):
	''' To be replaced with actual query results

	Should return a list of course dictionaries
		Ex: [{"title":"Info Systems", "description": "fun"}, {"title":"Other Course", "description":"less fun"}
	'''
	# RankedCoursesObj = RankedCourses(query)
	# ranked_courses_indeces = RankedCoursesObj.get_ranked_course_indeces()
	# return ranked_courses_indeces
	# [json_content[index] for index in ranked_courses_indeces]
	# return [x for x in json_content[:10]]
	RankedCoursesObj = ElasticsearchRankedCourses(query)
	results = RankedCoursesObj.run_query()
	return results


@irsystem.route('/', methods=['GET'])
def index():
	query = request.args.get('search')
	if not query:
		return render_template('index.html', name=project_name, netid=net_id)
	else:
		data = run_info_retrieval(query)
		output_message =  "Your search: " + query
		return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data, query=query)

@irsystem.route('/login', methods=['GET'])
def login():
	return render_template('login.html')

@irsystem.route('/saved', methods=['GET'])
def saved():
	return render_template('saved.html')
