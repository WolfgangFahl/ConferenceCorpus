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
        debug=False
        DataSourceTest.setUp(self,debug=debug)
        pass


    def testWikiCFP(self):
        '''
        test the WikiCFP lookup
        '''
        lookup=CorpusLookup(lookupIds=["wikicfp"])
        lookup.load(forceUpdate=False)
        wikiCfpDataSource=lookup.getDataSource("wikicfp")
        # TODO 89000 as of 2021-12-27
        self.checkDataSource(wikiCfpDataSource,6000,89800)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()