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
    
    def exportSeries(self,dblpSeriesId):
        '''
        '''

    def testSeriesExport(self):
        '''
        test exporting a single series
        '''
        # do not run this in CI
        if getpass.getuser()!="wf":
            return
        lookup=CorpusLookup(lookupIds=["dblp","wikidata","confref"])
        lookup.load(forceUpdate=False)
        dblpDataSource=lookup.getDataSource("dblp")
        confrefDataSource=lookup.getDataSource("confref")
        wikidataDataSource=lookup.getDataSource("wikidata")
        seriesByAcronym,_dup=wikidataDataSource.eventSeriesManager.getLookup("DBLP_pid")
    
        for acronym in [#'dc','ds'
                        #,'seke','qurator',
                        'vnc'
            ]:
            dblpSeriesId=f"conf/{acronym}"
            eventSeries=seriesByAcronym[dblpSeriesId]
            print(eventSeries.asWikiMarkup())
            eventBySeries=confrefDataSource.eventManager.getLookup("dblpSeriesId",withDuplicates=True)
            events=eventBySeries[dblpSeriesId]
            for event in events:
                print(event.asWikiMarkup(eventSeries.acronym))
            pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()