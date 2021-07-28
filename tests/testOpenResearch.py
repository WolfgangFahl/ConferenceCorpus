'''
Created on 27.07.2021

@author: wf
'''
import unittest
from sys import path

from lodstorage.storageconfig import StorageConfig

from tests.testSMW import TestSMW
from wikifile.wikiFileManager import WikiFileManager
from datasources.openresearch import OREvent,OREventManager,OREventSeries,OREventSeriesManager




class TestOpenResearch(unittest.TestCase):


    def setUp(self):
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
        eventManager.fromWikiFileManager(self.wikiFileManager)
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



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()