import requests

# format: https://classes.cornell.edu/api/2.0/<method>.<responseFormat>?parameters 
link = "https://classes.cornell.edu/api/2.0/config/rosters.json"

# this will send a get request for data from the link above
response = requests.get(link)

# print json output
print (response.json())