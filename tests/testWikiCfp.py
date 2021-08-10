'''
Created on 2021-07-31

@author: wf
'''
import unittest
from corpus.lookup import CorpusLookup
from tests.datasourcetoolbox import DataSourceTest

class TestWikiCFP(DataSourceTest):
    '''
    test WikiCFP data source
    '''

    def setUp(self):
        DataSourceTest.setUp(self)
        pass


    def testWikiCFP(self):
        '''
        test the WikiCFP lookup
        '''
        lookup=CorpusLookup(lookupIds=["wikicfp"])
        lookup.load(forceUpdate=True)
        wikiCfpDataSource=lookup.getDataSource("wikicfp")
        self.checkDataSource(wikiCfpDataSource,3000,87000)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()