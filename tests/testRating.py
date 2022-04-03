'''
Created on 2021-08-07

@author: wf
'''
import unittest
from corpus.lookup import CorpusLookup
from corpus.quality.rating import RatingManager
from tests.datasourcetoolbox import DataSourceTest
import getpass

class TestRating(DataSourceTest):
    '''
    test the rating handling
    '''

    def setUp(self, debug:bool=False, profile:bool=True, **kwargs):
        DataSourceTest.setUp(self, debug=debug, profile=profile, **kwargs)
        pass

    def testRating(self):
        '''
        test the rating
        '''
        # do not run this in CI
        if getpass.getuser()!="wf":
            return
        ratingManager=RatingManager()
        lookup=CorpusLookup(lookupIds=["wikicfp"])
        lookup.load()
        wikiCfpDataSource=lookup.getDataSource("wikicfp")
        wikiCfpDataSource.rateAll(ratingManager)
        #ratingManager.store()
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()