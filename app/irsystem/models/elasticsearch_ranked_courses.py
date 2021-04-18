
from elasticsearch import Elasticsearch, RequestsHttpConnection

# https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-mlt-query.html

class ElasticsearchRankedCourses:

    def __init__(self, query):
        self.es = Elasticsearch(
            hosts= "search-cornellcourserecommender-sqp7dbsc4owlrftw5cefn7lfjq.us-east-1.es.amazonaws.com",
            http_auth=("courserecs", "Cornell2021!"),
            port=443,
            use_ssl=True,
            connection_class=RequestsHttpConnection,
            scheme="https"
        )
        self.query = self.make_es_query(query)

    def make_es_query(self,  query):
        print(query)
        query_es = {
            "more_like_this" : {
                "fields" : ["description", "titleLong"],
                "like" : [query],
                "unlike" : ["abcdefg"],
                "min_term_freq" : 0,
                "max_query_terms" : 20,
                "max_doc_freq": 3500,
                "min_doc_freq" : 0,
                "stop_words": ["the"]
            }
        }
        return query_es

    def run_query(self):
        result = self.es.search(index="roster", body={"query": self.query})
        #print(result)
        try:
            hits = result['hits']['hits']
            hits_json =  [x['_source']  for x in hits]
        except Exception as e:
            print(e)
            hits_json =  []
        #print(hits_json)
        return hits_json
