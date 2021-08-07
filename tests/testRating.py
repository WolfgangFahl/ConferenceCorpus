'''
Created on 2021-08-07

@author: wf
'''
import unittest
from corpus.lookup import CorpusLookup
from quality.rating import RatingManager
from tests.datasourcetoolbox import DataSourceTest

class TestRating(DataSourceTest):
    '''
    test the rating handling
    '''

    def setUp(self):
        DataSourceTest.setUp(self)
        pass

    def testRating(self):
        '''
        test the rating
        '''
        ratingManager=RatingManager()
        lookup=CorpusLookup(lookupIds=["wikicfp"])
        lookup.load()
        wikiCfpDataSource=lookup.getDataSource("wikicfp")
        wikiCfpDataSource.rateAll(ratingManager)
        ratingManager.store()
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()