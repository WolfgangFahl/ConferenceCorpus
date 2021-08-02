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
        self.dblp=TestDblp.getDblp(self)
        pass
    
    def testDblp(self):
        '''
        test getting the conference series and events from dblp xml dump
        '''
        lookup=CorpusLookup(lookupIds=["dblp"])
        lookup.load()
        dblpDataSource=lookup.getDataSource("dblp")
        dblp=TestDblp.getMockedDblp(debug=self.debug)
        dblpDataSource.eventManager.dblp=dblp
        dblpDataSource.eventSeriesManager.dblp=dblp
        self.checkDataSource(dblpDataSource, 138 if self.mock else 5200,1000 if self.mock else 40000)    


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()