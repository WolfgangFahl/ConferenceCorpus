'''
Created on 28.07.2021

@author: wf
'''
import unittest
import tests.testDblpXml 
from corpus.datasources.dblp import Dblp
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup

class TestDblpEvents(DataSourceTest):
    '''
    test the dblp data source
    '''
 
    def setUp(self):
        '''
        setup 
        '''
        self.mock=tests.testDblpXml.TestDblp.mock 
        DataSourceTest.setUp(self)
        pass
    
    def configureCorpusLookup(self,lookup:CorpusLookup):
        '''
        callback to configure the corpus lookup
        '''
        dblpDataSource=lookup.getDataSource("dblp")
        dblpXml=tests.testDblpXml.TestDblp.getMockedDblp(mock=self.mock,debug=self.debug)
        dblpDataSource.eventManager.dblpXml=dblpXml
        dblpDataSource.eventSeriesManager.dblpXml=dblpXml
        
    
    def testDblp(self):
        '''
        test getting the conference series and events from dblp xml dump
        '''
        lookup=CorpusLookup(lookupIds=["dblp"],configure=self.configureCorpusLookup)
        lookup.load(forceUpdate=False)
        dblpDataSource=lookup.getDataSource("dblp")
        self.checkDataSource(dblpDataSource, 138 if self.mock else 5200,1000 if self.mock else 40000)    

    def testDateRange(self):
        '''
        test date Range parsing
        '''
        dblp=Dblp()
        dateStrings=['18-21 September 2005']
        for dateString in dateStrings:
            dateRange=dblp.getDateRange(dateString)
            print(dateRange)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()