'''
Created on 28.07.2021

@author: wf
'''
import unittest
from lodstorage.storageconfig import StorageConfig
from datasources.dblp import DblpEventSeriesManager,DblpEventManager
from tests import testDblpXml

class TestDblpEvents(unittest.TestCase):
    '''
    test the dblp data source
    '''
    def setUp(self):
        self.mock=testDblpXml.TestDblp.mock
        self.forceUpdate=False
        pass


    def tearDown(self):
        pass


    def testDblp(self):
        '''
        test getting the conference series and events from dblp xml dump
        '''
        config = StorageConfig.getSQL()
        dblp=testDblpXml.TestDblp.getDblp(self)
        dblpEventSeriesManager=DblpEventSeriesManager(config=config)
        dblpEventSeriesManager.dblp=dblp
        dblpEventSeriesManager.configure()
        dblpEventSeriesManager.fromCache(force=self.forceUpdate)
        esl = dblpEventSeriesManager.getList()
        if self.debug:
            print(f"Found {len(esl)} dblp event Series")
        if not dblpEventSeriesManager.isCached():
            dblpEventSeriesManager.store()
            
        expected=138 if self.mock else 5200
        self.assertTrue(len(esl) >= expected)
        
        dblpEventManager=DblpEventManager(config=config)
        dblpEventManager.dblp=dblp
        dblpEventManager.configure()
        dblpEventManager.fromCache(force=self.forceUpdate,getListOfDicts=dblpEventManager.getLoDfromDblp)
        el = dblpEventManager.getList()
        if self.debug:
            print(f"Found {len(el)} dblp events")
        if not dblpEventManager.isCached():
            dblpEventManager.store()
        expected=1000 if self.mock else 40000
        self.assertTrue(len(el) >= expected)
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()