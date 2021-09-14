'''
Created on 2021-08-07

@author: wf
'''

import unittest
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup
import getpass

class EventExporter():
    '''
    exporter for Events and series
    '''
    
    def __init__(self):
        '''
        construct me
        '''
        lookup=CorpusLookup(lookupIds=["dblp","wikidata","confref"])
        lookup.load(forceUpdate=False)
        self.dblpDataSource=lookup.getDataSource("dblp")
        self.confrefDataSource=lookup.getDataSource("confref")
        wikidataDataSource=lookup.getDataSource("wikidata")
        self.seriesByAcronym,_dup=wikidataDataSource.eventSeriesManager.getLookup("DBLP_pid")
    
    def exportSeries2OpenResearch(self,dblpSeriesId):
        '''
        export the seriew with the given dblp Series Id to OpenResearch
        '''
        eventSeries=self.seriesByAcronym[dblpSeriesId]
        print(eventSeries.asWikiMarkup())
        eventBySeries=self.confrefDataSource.eventManager.getLookup("dblpSeriesId",withDuplicates=True)
        events=eventBySeries[dblpSeriesId]
        for event in events:
            print(event.asWikiMarkup(eventSeries.acronym))

class TestOpenResearchExport(DataSourceTest):
    '''
    test the dblp data source
    '''
 
    def setUp(self):
        '''
        '''
        DataSourceTest.setUp(self)
        pass
  

    def testSeriesExport(self):
        '''
        test exporting a single series
        '''
        # do not run this in CI
        if getpass.getuser()!="wf":
            return
        exporter=EventExporter()
        for acronym in [#'dc','ds'
                        #,'seke','qurator',
                        #'vnc'
                        'dawak'
            ]:
            dblpSeriesId=f"conf/{acronym}"
            exporter.exportSeries2OpenResearch(dblpSeriesId)
            pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()