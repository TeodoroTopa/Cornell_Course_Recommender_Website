
# https://towardsdatascience.com/python-and-postgresql-how-to-access-a-postgresql-database-like-a-data-scientist-b5a9c5a0ea43

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json

def obtain_col_types(cols):
    return {
        "crseId": "INT",
        "crseOfferNbr": "INT",
        "subject": "TEXT",
        "catalogNbr": "TEXT",
        "titleLong": "TEXT",
        "description": "TEXT", 
        "catalogForbiddenOverlaps": "TEXT",
        "catalogAttribute": "TEXT",
        "catalogWhenOffered": "TEXT",
        "catalogComments": "TEXT",
        "catalogPrereqCoreq": "TEXT",
        "catalogFee": "TEXT",
        "catalogSatisfiesReq": "TEXT",
        "catalogPermission": "TEXT",
        "catalogCourseSubfield": "TEXT",
        "acadCareer": "TEXT",
        "acadGroup": "TEXT",
        "unitsMinimum": "INT",
        "unitsMaximum": "INT",
        "componentsRequired": "TEXT", # fix this
        "gradingBasis": "TEXT",
        "gradingBasisLong": "TEXT",
        "sessionBeginDt": "TEXT",
        "sessionEndDt": "TEXT",
        "sessionLong": "TEXT",
        "ssrComponentLong": "TEXT",
        "classNbr": "INT",
        "locationDescr": "TEXT",
        "startDt": "TEXT",
        "endDt": "TEXT",
        "instructionMode": "TEXT",
        "instrModeDescr": "TEXT",
        "timeStart": "TEXT",
        "timeEnd": "TEXT",
        "startDt_copy": "TEXT",
        "endDt_copy": "TEXT",
        "pattern": "TEXT",
        "facilityDescr": "TEXT",
        "bldgDescr": "TEXT",
        "netid": "TEXT",
        "firstName": "TEXT",
        "middleName": "TEXT",
        "lastName": "TEXT",
        "descrlong": "TEXT"
    }

def get_data_from_db():

    ''' connect to database '''
    ''' note that these credentials may need to change '''
    DATABASE_URL = os.environ['DATABASE_URL']
    # url = make_url(DATABASE_URL)
    DB_NAME = "d3ugti6oa37ph0"
    DB_PORT = 5432
    DB_USER = "debyvgrybtgvto"
    DB_PASS = "255373b7ad411efa03ee0231d2c99945840266ac45b85e6144429afeea62e919"
    DB_HOST = "ec2-52-23-45-36.compute-1.amazonaws.com"

    conn = psycopg2.connect(dbname=DB_NAME, port=DB_PORT, user=DB_USER, password=DB_PASS, host=DB_HOST)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    ''' creating a cursor object '''
    cur = conn.cursor()

    ''' select - to test '''
    cur.execute('''SELECT * FROM CLASS''')
    result = cur.fetchall()
    # print(result)

    ''' Commit your changes in the database '''
    conn.commit()

    cur.close()
    conn.close()

    return result

def add_new_id(initial_data):
    return None


    # create a dictionary to store unique crseIDs
    # K = (titleLong, description), and V = (crseID)
    # this info will be appended to our current tuple



def get_info_from_s3():
    course_contents = []
    if len(course_contents) == 0:
        print("Retrieving course contents from s3...")
        course_contents = get_course_data()
    print (course_contents)
    return course_contents


if __name__ == "__main__":
    # initial_data = get_data_from_db()
    # add_new_id(initial_data)
    get_info_from_s3()

