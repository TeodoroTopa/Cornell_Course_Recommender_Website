import requests

# # format: https://classes.cornell.edu/api/2.0/<method>.<responseFormat>?parameters
# link = "https://classes.cornell.edu/api/2.0/config/rosters.json"
#
# # this will send a get request for data from the link above
# response = requests.get(link)
#
# # print json output
# print (response.json())

#Base URL for requests
BASIS_URL = "https://classes.cornell.edu/api/2.0/"
#All available methods.
#   1. Returns meta data on rosters available ex. "SP21",
#   2. Levels "Graduate, Undergraduate etc.
#   3. Different schools available "Engineering, Architecture and Planning" etc.
#   4. Returns 1000, 2000, 3000, 4000 etc. (Not very useful?)
#   5. All cornell subjects / majors (I think) "Asian American Studies,Architecture,..." etc.
#   6.

METHODS = ["config/rosters","config/acadCareers","config/acadGroups","config/classLevels","config/subjects","search/classes"]
#Potential method arguments. Ex: "roster" can be specified for method config/acadCareers
METHODS_ARG = ["","roster","roster","roster,subject","roster,subject,acadCareer,classLevels","roster,subject,crseAttrs"]
#Standard format for requests, XL also exists
STD_FORMAT = ".json"
class Roster():
    def __init__(self):
        self.course_json = self.basic_json_extractor(method="config/rosters",parameters=None)
        self.available_years_dict = self.available_rosters(self.course_json)

    def basic_json_extractor(self,method="config/rosters",parameters=None):
        """
        Input:
            method: str API method
            parameters: str or list for API method
        Output:
            extracted json

        From API descrip: https://<HOST>/api/<VERSION>/<method>.<responseFormat>?parameters
        https://<HOST>/api/<VERSION>/ is found in global variable BASIS_URL
        <responseFormat> is found in global variable STD_FORMAT
        """
        if type(parameters) == str:
            request = requests.get(BASIS_URL+method+STD_FORMAT+"?roster="+parameters)
        elif type(parameters) == list:
            arg = "?roster="+parameters[0]+"&subject="+parameters[1] #terrible code I know. I will fix later -Mads
            request = requests.get(BASIS_URL + method + STD_FORMAT + arg)
        else:
            request = requests.get(BASIS_URL + method + STD_FORMAT)
        json = request.json()
        return json

    def available_rosters(self,course_json):
        """
        Input:
            course_json: Response (standard requests.get(link), where link is .../config/rosters.json)
        Output:
            Dictionary with roster as key (ex. FA15), and idx as value
        """
        years = [(course_json['data']['rosters'][idx]['slug'], idx) for idx, year in
                 enumerate(range(len(course_json['data']['rosters'])))]
        return dict(years)

    # def extract_meta_info(self,course_json, year = "SP21"):
    # """
    # Input:
    #     course_json: Response (standard requests.get(link), where link is .../config/rosters.json)
    #     year = str ex. <SP21>
    # Output:
    #     dictionary with description, location & campus
    # """
    #     idx = self.available_years_dict[year]
    #     r_year = course_json['data']['rosters'][idx]
    #     return {"desc": r_year["descr"],"loc": r_year['defaultLocation'],"campus": r_year['defaultCampus'] }
    #
    def extract_course_rosterv0(self):
        roster_json = self.basic_json_extractor()
        test_year = 'SP21'
        subjects_json = self.basic_json_extractor(method=METHODS[4],parameters=test_year)['data']['subjects']
        test_subject = subjects_json[48]['value'] #Computer science

        classes = self.basic_json_extractor(method=METHODS[5],parameters=[test_year,test_subject])
        # self.extract_meta_info(roster_json,test_year)
        a = 2
        return 0


if __name__ == "__main__":
    roster = Roster()


    temp_data = roster.extract_course_rosterv0()