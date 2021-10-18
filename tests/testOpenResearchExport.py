'''
Created on 2021-08-07

@author: wf
'''

import unittest
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup
from corpus.datasources.openresearch import OREvent
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
        self.wikiDataSeriesByDblpPid,_dup=wikidataDataSource.eventSeriesManager.getLookup("DBLP_pid")
        self.dblpSeriesById,_dup=self.dblpDataSource.eventSeriesManager.getLookup("eventSeriesId")
        self.orTemplateParamLookup=OREvent.getTemplateParamLookup()
    
    def exportSeries2OpenResearch(self,dblpSeriesId):
        '''
        export the seriew with the given dblp Series Id to OpenResearch
        
        Args:
            dblpSeriesId(str): the id of the dblp series to be exported
            
        Return:
            int: the number of events exported
        '''
        dblpSeriesPid=f"conf/{dblpSeriesId}"
        count=0
        if dblpSeriesId in self.dblpSeriesById:
            eventSeries=self.dblpSeriesById[dblpSeriesId]
            print(eventSeries.asWikiMarkup())
            eventBySeries=self.dblpDataSource.eventManager.getLookup("series",withDuplicates=True)
            events=eventBySeries[dblpSeriesId]
            for event in events:
                print(event.asWikiMarkup(eventSeries.acronym,self.orTemplateParamLookup))
                count+=1
        return count
            

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
                        #'dawak','emnlp','cla'
                        #'ijcnn'
                        #'recsys'
                        'ideas'
            ]:
            dblpSeriesId=f"{acronym}"
            self.assertTrue(exporter.exportSeries2OpenResearch(dblpSeriesId)>0)
            pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()