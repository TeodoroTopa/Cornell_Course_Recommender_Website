
# https://towardsdatascience.com/python-and-postgresql-how-to-access-a-postgresql-database-like-a-data-scientist-b5a9c5a0ea43

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json


def obtain_col_info(current_cols):
    ret_lst = []

    for key in (current_cols['binary, keep == 1'].keys()):
        val = current_cols['binary, keep == 1'][key]
        if (current_cols['binary, keep == 1'][key] == 1):
            input = current_cols['column name'][key]
            input = input[2:len(input) - 1]
            ret_lst.append(input)
    
    return ret_lst

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

def generate_arg_string_formats(col_with_types):
    ret = ""
    for key in col_with_types.keys():
        value = col_with_types[key]
        # if (value == "TEXT"):
        ret += "%s,"
        # if (value == "INT"):
        #     ret += "%d,"
    return ret[:len(ret)-1]

def load_data(course_json, cols_desired, cols_with_types_dict):
    ret = [] # list of tuples containing necessary fields
    for course in course_json:
        output = list()
        for col in cols_desired:
            if (course[col] == None):
                if (cols_with_types_dict[col] == "TEXT"):
                    output.append("None")
                else:
                    output.append(-1)
            elif (col == "componentsRequired"): 
                val = course[col]
                if (isinstance(val, str)):
                    output.append(course[col])
                else:
                    v = ' '.join(course[col])
                    output.append(v)
            else:
                output.append(course[col])
        ret.append(tuple(output))
    
    return ret

''' connect to database '''
''' note that these credentials may need to change '''
DATABASE_URL = os.environ['DATABASE_URL']
DB_NAME = "d79u63b2cbg9om"
DB_PORT = 5432
DB_USER = "kugnzgerojalup"
DB_PASS = "f4c347af5b4f5818e118cf656221324546d81dd0c539cd588f9f80e9bf7ecdc9"
DB_HOST = "ec2-54-211-176-156.compute-1.amazonaws.com"

conn = psycopg2.connect(dbname=DB_NAME, port=DB_PORT, user=DB_USER, password=DB_PASS, host=DB_HOST)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

''' creating a cursor object '''
cur = conn.cursor()

''' load json info now '''
with open('ManualColumnPicking.json') as f: rows_include = json.load(f)
with open('course_data.json') as f: course_info = json.load(f)

''' NOTE: do not forget to [heroku login] before starting '''
# here: extract columns that we want to put into our database
cols = obtain_col_info(rows_include)

# in this list, we need to assign specific types for everything
# returns dictionary we can then use to create a string
# to then form a string to input
cols_with_types = obtain_col_types(cols)

cols_with_types_string = ""
for key in cols_with_types.keys():
    cols_with_types_string += key + " " + cols_with_types[key] + ","

sql = "CREATE TABLE CLASS(" + cols_with_types_string[:len(cols_with_types_string)-1] + ")"
print (sql)
cur.execute(sql)
print("Table created successfully........")

''' insert into database '''
insert_stmt = (
    "INSERT INTO CLASS(" + ','.join(map(str, cols)) + ") " + 
    "VALUES (" + generate_arg_string_formats(cols_with_types) + ")" 
)
print (insert_stmt)
    
data=load_data(course_info, cols, cols_with_types)

''' Executing the SQL command '''
for d in data:
    # print (insert_stmt, d)
    cur.execute(insert_stmt, d)

''' Commit your changes in the database '''
conn.commit()

''' select - to test '''
cur.execute('''SELECT * FROM CLASS''')
result = cur.fetchall()
print(result)

''' Commit your changes in the database '''
conn.commit()

cur.close()
conn.close()
