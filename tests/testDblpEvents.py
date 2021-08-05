'''
Created on 28.07.2021

@author: wf
'''
import unittest
from tests.testDblpXml import TestDblp
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup

class TestDblpEvents(DataSourceTest):
    '''
    test the dblp data source
    '''
 
    def setUp(self):
        '''
        '''
        self.mock=TestDblp.mock
        DataSourceTest.setUp(self)
        pass
    
    def configureCorpusLookup(self,lookup:CorpusLookup):
        '''
        callback to configure the corpus lookup
        '''
        dblpDataSource=lookup.getDataSource("dblp")
        dblpXml=TestDblp.getMockedDblp(debug=self.debug)
        dblpDataSource.eventManager.dblpXml=dblpXml
        dblpDataSource.eventSeriesManager.dblpXml=dblpXml
        
    
    def testDblp(self):
        '''
        test getting the conference series and events from dblp xml dump
        '''
        lookup=CorpusLookup(lookupIds=["dblp"],configure=self.configureCorpusLookup)
        lookup.load(forceUpdate=False)
        dblpDataSource=lookup.getDataSource("dblp")
        dblpXml=TestDblp.getMockedDblp(debug=self.debug)
        dblpDataSource.eventManager.dblpXml=dblpXml
        dblpDataSource.eventSeriesManager.dblpXml=dblpXml
        self.checkDataSource(dblpDataSource, 138 if self.mock else 5200,1000 if self.mock else 40000)    


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()