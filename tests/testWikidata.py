'''
Created on 27.07.2021

@author: wf
'''
import unittest
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup

class TestWikiData(DataSourceTest):
    '''
    test wiki data access
    '''

    def setUp(self):
        DataSourceTest.setUp(self)
        pass

    def testWikidata(self):
        '''
        test getting the wikiData Event Series
        '''
        lookup=CorpusLookup(lookupIds=["wikidata"])
        wikidataDataSource=lookup.getDataSource("wikidata")
        self.checkDataSource(wikidataDataSource,4200,7400)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()