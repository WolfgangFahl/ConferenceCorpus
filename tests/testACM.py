'''
Created on 04.11.2021

@author: wf
'''
import unittest
from lodstorage.query import Query
from corpus.datasources.acm import ACM,AcmEvent,AcmEventSeries
import copy
from tests.datasourcetoolbox import DataSourceTest

from lodstorage.sparql import SPARQL

class TestACM(DataSourceTest):
    '''
    test getting events from the ACM digital library
    '''

    def setUp(self):
        DataSourceTest.setUp(self)
        pass

    def testACM(self):
        '''
        see issue https://github.com/WolfgangFahl/ConferenceCorpus/issues/17
        '''
        if self.inCI():
            return
        debug=True
        acm=ACM(debug=debug,showHtml=False)
        # example https://dl.acm.org/event.cfm?id=RE149
        for acmDlEventId in ["RE149"]:
            acmSeries=acm.eventSeriesfromDigitalLibraryEventId(acmDlEventId)
        # example https://dl.acm.org/doi/proceedings/10.1145/3149869
        for doi in ["10.1145/3209281","10.1145/3149869"]:
            acmEvent=acm.eventFromProceedingsDOI(doi)
        pass
    
    def testACMWikidata(self):
        '''
        see https://github.com/WolfgangFahl/ConferenceCorpus/issues/17
        '''
        queryString="""# WF 2021-11-04
# ACM events in Wikidata
SELECT ?event ?eventLabel ?acmConferenceId ?acmEventId ?dblpEventId ?type ?typeLabel WHERE {
  #?event wdt:P31 wd:Q52260246.  
  ?event wdt:P31 ?type.
  ?event wdt:P7979 ?acmConferenceId.
  ?event wdt:P3333 ?acmEventId.
  OPTIONAL  {
    ?event wdt:P8926 ?dblpEventId.
  }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER by ?acmEventId"""
        endpoint="https://query.wikidata.org/sparql"
        wd=SPARQL(endpoint)
        qlod=wd.queryAsListOfDicts(queryString,fixNone=True)
        query=Query(name="ACM DL Events",query=queryString,lang='sparql')
        debug=self.debug
        debug=True
        for tablefmt in ["github","mediawiki","latex"]:
            lod=copy.deepcopy(qlod)
            qdoc=query.documentQueryResult(lod,tablefmt=tablefmt)
            if debug:
                print (qdoc)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()