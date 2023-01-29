'''
Created on 2023-01-23

@author: wf
'''
from tests.basetest import BaseTest
from corpus.event import EventStorage
from lodstorage.sparql import SPARQL
from lodstorage.query import EndpointManager
import json

class TestDblpSparql(BaseTest):
    """
    test the dblp SPARQL query
    """
    def setUp(self, debug=False, profile=True):
        BaseTest.setUp(self, debug=debug, profile=profile)
        self.dblpQueryManager=EventStorage.getQueryManager(lang="sparql",name="dblp")
        self.wikidataQueryManager=EventStorage.getQueryManager(lang="sparql",name="wikidata")
    
    def testDblpEventsQuery(self):
        """
        test the DBLP Events SPARQL Query
        """       
        query=self.dblpQueryManager.queriesByName["dblp-Events"]
        debug=True
        if debug:
            print(query)
        for endpoint in ["https://qlever.cs.uni-freiburg.de/api/dblp"]:
            sparql=SPARQL(endpoint)
            sparql_query=query.query
            sparql_query=sparql_query.replace("#FILTER","FILTER")
            records=sparql.queryAsListOfDicts(sparql_query)
            if debug:
                print(json.dumps(records,indent=2))
            pass
        
    def testDblpSeriesAcronyms4Series(self):
        """
        test Dblp Series Acronyms
        """
        endpoints=EndpointManager.getEndpoints(lang="sparql")
        dblpQuery=self.dblpQueryManager.queriesByName["dblp-EventSeries"]
        wikidataQuery=self.wikidataQueryManager.queriesByName["WikidataDblpEventSeries"]
        acronyms=0
        counts=[]
        debug=self.debug
        debug=True
        for en,query in [("dblp",dblpQuery),("qlever-wikidata",wikidataQuery)]:
            endpointConf=endpoints[en]
            sparql=SPARQL.fromEndpointConf(endpointConf) 
            sparql_query=query.query
            records=sparql.queryAsListOfDicts(sparql_query)
            count=len(records)
            counts.append(count)
            print(f"{query.name}:{count}")
            if query.name=="WikidataDblpEventSeries":
                for record in records:
                    if "short_name" in record:
                        acronyms+=1
        total=counts[0]
        wikidata=counts[1]
        print(f"""{wikidata}/{total}={wikidata/total*100:.1f}%""")
        print(f"""{acronyms}/{total}={acronyms/total*100:.1f}%""") 