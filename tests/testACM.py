'''
Created on 04.11.2021

@author: wf
'''
import unittest
from lodstorage.query import Query
from corpus.lookup import CorpusLookup
from corpus.datasources.acm import ACM,AcmEvent,AcmEventSeries
import copy
from corpus.datasources.wikidata import Wikidata
from tests.datasourcetoolbox import DataSourceTest

from lodstorage.sparql import SPARQL

class TestACM(DataSourceTest):
    '''
    test getting events from the ACM digital library
    '''

    def setUp(self):
        DataSourceTest.setUp(self)
        self.lookup=CorpusLookup(lookupIds=["acm"])
        self.lookup.load(forceUpdate=True)
        self.acmDataSource=self.lookup.getDataSource("acm")
        pass
    
    def testACMDataSource(self):
        self.checkDataSource(self.acmDataSource,1,1)

    def testACM(self):
        '''
        see issue https://github.com/WolfgangFahl/ConferenceCorpus/issues/17
        '''
        if self.inCI():
            return
        debug=self.debug
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
        acmSeriesManager=self.acmDataSource.eventSeriesManager
        queryString=acmSeriesManager.getSparqlQuery()
        endpoint=Wikidata.endpoint
        wd=SPARQL(endpoint)
        qlod=wd.queryAsListOfDicts(queryString,fixNone=True)
        query=Query(name="ACM DL Events",query=queryString,lang='sparql')
        show=self.debug
        show=True
        for tablefmt in ["github","mediawiki","latex"]:
            qdoc=query.documentQueryResult(qlod,tablefmt=tablefmt)
            if show:
                print (qdoc)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()