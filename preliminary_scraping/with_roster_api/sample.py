import requests
import pandas as pd,os

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
#   6. returns classed for a subject for a specific year

METHODS = ["config/rosters","config/acadCareers","config/acadGroups","config/classLevels","config/subjects","search/classes"]
#Potential method arguments. Ex: "roster" can be specified for method config/acadCareers
METHODS_ARG = ["","roster","roster","roster,subject","roster,subject,acadCareer,classLevels","roster,subject,crseAttrs"]
#Standard format for requests, XL also exists
STD_FORMAT = ".json"
ROSTER_PERIOD = 'SP21'
class Roster():
    def __init__(self):
        #Method 1
        self.course_json = self.basic_json_extractor(method=METHODS[0],parameters=None)
        self.available_years_dict = self.available_rosters(self.course_json)
        self.subjects_json = self.basic_json_extractor(method=METHODS[4],parameters=ROSTER_PERIOD)['data']['subjects']


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
        test_subject = self.subjects_json[48]['value'] #Computer science
        classes = self.basic_json_extractor(method=METHODS[5],parameters=[ROSTER_PERIOD,test_subject])
        # self.extract_meta_info(roster_json,test_year)
        data = classes['data']['classes']
        dataFrame = pd.DataFrame.from_dict(data)

        a = 2
        return 0

    def extract_course_rosterv1(self,year=ROSTER_PERIOD,subject=None):
        df = pd.DataFrame()
        if type(subject) == type(None):
            for i in range(len(self.subjects_json)):
                temp_sub = self.subjects_json[i]['value']
                classes = self.basic_json_extractor(method=METHODS[5], parameters=[ROSTER_PERIOD, temp_sub])
                temp_data = classes['data']['classes']
                temp_dataFrame = pd.DataFrame.from_dict(temp_data)
                df = df.append(temp_dataFrame, ignore_index=True)
        else:
            classes = self.basic_json_extractor(method=METHODS[5], parameters=[ROSTER_PERIOD, subject])
            data = classes['data']['classes']
            dataFrame = pd.DataFrame.from_dict(data)

        return df

    def save_df(self,df,path=os.getcwd(),filename="course_data"):
        df.to_json(os.path.join(path,filename))

if __name__ == "__main__":
    roster = Roster()
    SP21_data = roster.extract_course_rosterv1()
    roster.save_df(SP21_data)
