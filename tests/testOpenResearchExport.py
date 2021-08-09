'''
Created on 2021-08-07

@author: wf
'''

import unittest
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup
import getpass

class TestOpenResearchExport(DataSourceTest):
    '''
    test the dblp data source
    '''
 
    def setUp(self):
        '''
        '''
        DataSourceTest.setUp(self)
        pass

    def testDblpSeriesExport(self):
        '''
        test exporting a single series
        '''
        # do not run this in CI
        if getpass.getuser()!="wf":
            return
        lookup=CorpusLookup(lookupIds=["dblp"])
        lookup.load(forceUpdate=False)
        dblpDataSource=lookup.getDataSource("dblp")
        seriesByAcronym,_dup=dblpDataSource.eventSeriesManager.getLookup("acronym")
    
        for acronym in ['seke','qurator']:
            eventSeries=seriesByAcronym[acronym]
            print(eventSeries.asWikiMarkup())
            eventBySeries=dblpDataSource.eventManager.getLookup("series",withDuplicates=True)
            events=eventBySeries[acronym]
            for event in events:
                print(event.asWikiMarkup())
            pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()