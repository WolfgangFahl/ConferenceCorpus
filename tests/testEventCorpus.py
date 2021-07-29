'''
Created on 2021-07-26

@author: wf
'''
import unittest
from corpus.eventcorpus import EventCorpus
from datasources.dblp import DblpEventManager,DblpEventSeriesManager
from datasources.wikidata import WikidataEventManager,WikidataEventSeriesManager


class TestEventCorpus(unittest.TestCase):
    '''
    test the event corpus
    '''

    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testEventCorpus(self):
        '''
        test the eventCorpus
        '''
        eventCorpus=EventCorpus()
        eventCorpus.addDataSource("dblp",DblpEventManager(),DblpEventSeriesManager())
        eventCorpus.addDataSource("wikidata",WikidataEventManager(),WikidataEventSeriesManager())
        eventCorpus.loadAll()
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()