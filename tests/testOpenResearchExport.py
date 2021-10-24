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
        count=0
        if dblpSeriesId in self.dblpSeriesById:
            eventSeries=self.dblpSeriesById[dblpSeriesId]
            eventBySeries=self.dblpDataSource.eventManager.getLookup("series",withDuplicates=True)
            events=eventBySeries[dblpSeriesId]
            count=self.exportSeries2OpenRessearch(eventSeries, events)
        return count
            
    def exportSeries2OpenRessearch(self,eventSeries,events):
        '''
        Args:
            eventSeries(EventSeries): the series to export
            events(list): the list of events to export
        Return:
            int: the number of events exported
        '''
        count=0
        for event in events:
            pass
        markup=eventSeries.asWikiMarkup()
        print(markup)
        for event in events:
            markup=event.asWikiMarkup(eventSeries.acronym,self.orTemplateParamLookup)
            print(markup)
            count+=1
        return count
            

class TestOpenResearchExport(DataSourceTest):
    '''
    test exporting series and events from the  dblp data source
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
        for acronym in ['dc'
                        #,'ds'
                        #,'seke','qurator',
                        #'vnc'
                        #'dawak','emnlp','cla'
                        #'ijcnn'
                        #'recsys'
                        #'ideas'
                        #'er'
            ]:
            dblpSeriesId=f"{acronym}"
            exportCount=exporter.exportSeries2OpenResearch(dblpSeriesId)
            self.assertTrue(exportCount>0)
            pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()