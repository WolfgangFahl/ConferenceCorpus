'''
Created on 27.07.2021

@author: wf
'''
import unittest
from lodstorage.storageconfig import StorageConfig
from tests.testSMW import TestSMW
from datasources.openresearch import OREventManager, OREventSeriesManager, OREventCorpus


class TestOpenResearch(unittest.TestCase):
    '''
    test the access to OpenResearch
    
    '''

    def setUp(self):
        self.debug=False
        self.forceUpdate=False
        self.wikiFileManager=TestSMW.getWikiFileManager()
        self.wikiuser=TestSMW.getWikiUser()

    def tearDown(self):
        pass

    def testOREventManagerFromWikiFileManager(self):
        '''
        tests the getting conferences form wiki markup files
        '''
        config = StorageConfig.getSQL()
        eventManager=OREventManager(config=config)
        eventManager.wikiFileManager=self.wikiFileManager
        eventManager.configure()
        eventManager.fromWikiFileManager()
        events=eventManager.getList()
        self.assertTrue(len(events)>8000)

    def testOREventSeriesManagerFromWikiFileManager(self):
        '''
        tests the getting conference series form wiki markup files
        '''
        config = StorageConfig.getSQL()
        eventSeriesManager=OREventSeriesManager(config=config)
        eventSeriesManager.fromWikiFileManager(self.wikiFileManager)
        eventSeries=eventSeriesManager.getList()
        self.assertTrue(len(eventSeries)>1000)

    def testOREventManagerFromWikiUser(self):
        '''
        tests the getting conferences form wiki markup files
        '''
        config = StorageConfig.getSQL()
        eventManager=OREventManager(config=config)
        eventManager.fromWikiUser(self.wikiuser)
        events=eventManager.getList()
        self.assertTrue(len(events)>8000)

    def testOREventSeriesManagerFromWikiUser(self):
        '''
        tests the getting conference series form wiki markup files
        '''
        config = StorageConfig.getSQL()
        eventSeriesManager=OREventSeriesManager(config=config)
        eventSeriesManager.fromWikiUser(self.wikiuser)
        eventSeries=eventSeriesManager.getList()
        self.assertTrue(len(eventSeries)>1000)

    def testOREventCorpus(self):
        '''
        tests initializing the OREventCorpus from wiki markup files
        '''
        config = StorageConfig.getSQL()
        corpus=OREventCorpus(config, self.debug)
        corpus.fromWikiFileManager(self.wikiFileManager)
        self.assertTrue(len(corpus.eventManager.getList()) > 8000)
        self.assertTrue(len(corpus.eventSeriesManager.getList()) > 1000)

    def testOREventCorpusFromWikiUser(self):
        '''
        tests initializing the OREventCorpus from wiki
        '''
        config = StorageConfig.getSQL()
        corpus=OREventCorpus(config, self.debug)
        corpus.fromWikiUser(self.wikiuser)
        self.assertTrue(len(corpus.eventManager.getList()) > 8000)
        self.assertTrue(len(corpus.eventSeriesManager.getList()) > 1000)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()