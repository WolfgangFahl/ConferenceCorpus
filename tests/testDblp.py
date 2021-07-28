'''
Created on 28.07.2021

@author: wf
'''
import unittest
from lodstorage.storageconfig import StorageConfig
from datasources.dblp import Dblp
from datasources.dblp import DblpEventSeriesManager,DblpEventManager

class TestDblp(unittest.TestCase):
    '''
    test the dblp data source
    '''
    def setUp(self):
        self.forceUpdate=True
        pass


    def tearDown(self):
        pass


    def testDblp(self):
        '''
        test getting the conference series and events from dblp xml dump
        '''
        config = StorageConfig.getSQL()
        dblp=Dblp(verbose=True)
        dblpEventSeriesManager=DblpEventSeriesManager(config=config,dblp=dblp)
        
        dblpEventSeriesManager.fromCache(force=self.forceUpdate,getListOfDicts=dblpEventSeriesManager.getLoDfromDblp)
        esl = dblpEventSeriesManager.getList()
        if self.debug:
            print(f"Found {len(esl)} dblp event Series")
        if not dblpEventSeriesManager.isCached():
            dblpEventSeriesManager.store()
        self.assertTrue(len(esl) > 5200)
        
        dblpEventManager=DblpEventManager(config=config,dblp=dblp)
        dblpEventManager.fromCache(force=self.forceUpdate,getListOfDicts=dblpEventManager.getLoDfromDblp)
        el = dblpEventManager.getList()
        if self.debug:
            print(f"Found {len(el)} dblp events")
        if not dblpEventManager.isCached():
            dblpEventManager.store()
        self.assertTrue(len(el) > 40000)
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()