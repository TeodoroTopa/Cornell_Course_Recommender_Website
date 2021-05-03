
# https://towardsdatascience.com/python-and-postgresql-how-to-access-a-postgresql-database-like-a-data-scientist-b5a9c5a0ea43

import json

''' read in json file [course_data.json] '''

f = open('course_data.json',)
data = json.load(f)

# Closing file
f.close()


''' have a course dictionary containing
    K = (title, description), V = crseID
'''
course_dict = dict()

new_json_file = ""
'''append new dictionary field "ourID" to current dictionary
    that accounts for any cross-listed classes
'''
for i in range(0,len(data)):
    i_title = data[i]['titleLong']
    i_desc = data[i]['description']
    i_crseId = data[i]['crseId']
    key = (i_title, i_desc)

    if (key in course_dict.keys()):
        data[i]['ourId'] = course_dict[key]

    else:
        data[i]['ourId'] = i_crseId
        course_dict[key] = i_crseId

# write file back out as json
with open('data_output.json', 'w') as outfile:
    json.dump(data, outfile)