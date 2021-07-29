'''
Created on 2021-07-26

@author: wf
'''
import unittest
from corpus.lookup import CorpusLookup


class TestEventCorpus(unittest.TestCase):
    '''
    test the event corpus
    '''

    def setUp(self):
        pass


    def tearDown(self):
        pass

    def testLookup(self):
        '''
        test the lookup
        '''
        lookup=CorpusLookup()
        lookup.load()
        self.assertEqual(2,len(lookup.eventCorpus.eventDataSources))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()