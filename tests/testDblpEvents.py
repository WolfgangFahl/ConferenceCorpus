'''
Created on 28.07.2021

@author: wf
'''
import unittest
from tests.testDblpXml import TestDblp
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup
import getpass

class TestDblpEvents(DataSourceTest):
    '''
    test the dblp data source
    '''
 
    def setUp(self):
        '''
        setup 
        '''
        self.mock=False if getpass.getuser()=="wf" else TestDblp.mock 
        DataSourceTest.setUp(self)
        pass
    
    def configureCorpusLookup(self,lookup:CorpusLookup):
        '''
        callback to configure the corpus lookup
        '''
        dblpDataSource=lookup.getDataSource("dblp")
        dblpXml=TestDblp.getMockedDblp(mock=self.mock,debug=self.debug)
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


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()