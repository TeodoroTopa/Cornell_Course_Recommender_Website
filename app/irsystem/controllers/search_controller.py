from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "Cornell Course Recommender"
net_id = "Marina Cheng (mkc236), Joanna Saikali (js3548), Yanchen Zhan (yz366), Mads Christian Berggrein Andersen (mba93), Teodoro Topa (tst42)"

import boto3
import botocore
from botocore import UNSIGNED
from botocore.config import Config

# BUCKET_NAME = 'cornell-course-data-bucket'
PATH = 'course_data.json'

# s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED))
json_content = []

# Getting Course Data
@irsystem.before_first_request
def get_course_data():

	BUCKET_NAME = 'cornell-course-data-bucket'
	s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED))

	try:
		content_object = s3.Object(BUCKET_NAME, PATH)
		file_content = content_object.get()['Body'].read().decode('utf-8')
		json_content = json.loads(file_content)
	except botocore.exceptions.ClientError as e:
		if e.response['Error']['Code'] == "404":
			print("The object does not exist.")
		else:
			raise

def run_info_retrieval(query):
	''' To be replaced with actual query results

	Should return a list of course dictionaries
		Ex: [{"title":"Info Systems", "description": "fun"}, {"title":"Other Course", "description":"less fun"}
	'''

	return [x for x in json_content[:10]]


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
