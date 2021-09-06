'''
Created on 05.09.2021

@author: wf
'''
import unittest
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup
from corpus.datasources.gnd import GND
import math
    
class TestGnd(DataSourceTest):
    '''
    test getting conference information from Gemeinsame Normdatei
    '''
    
    def setUp(self):
        super().setUp(debug=True)

    def testGnd(self):
        '''
        test getting conference information from Gemeinsame Normdatei
        '''
        lookup=CorpusLookup(lookupIds=["gnd"])
        
        lookup.load(forceUpdate=False)
        wikidataDataSource=lookup.getDataSource("gnd")
        expected=min(GND.limit,6000)
        self.checkDataSource(wikidataDataSource,1,expected)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()