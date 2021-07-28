'''
Created on 27.07.2021

@author: wf
'''
import unittest
from datasources.wikidata import WikidataEventSeriesManager,WikidataEventManager
from lodstorage.storageconfig import StorageConfig

class TestWikiData(unittest.TestCase):
    '''
    test wiki data access
    '''

    def setUp(self):
        self.debug=True
        self.forceUpdate=True
        pass


    def tearDown(self):
        pass


    def testWikidata(self):
        '''
        test getting the wikiData Event Series
        '''
        config=StorageConfig.getSQL()
        wesm=WikidataEventSeriesManager(config=config)
        wesm.fromCache(force=self.forceUpdate,getListOfDicts=wesm.getLoDfromEndpoint)
        esl=wesm.getList()
        if self.debug:
            print(f"Found {len(esl)} Wikidata event Series")
        self.assertTrue(len(esl)>4200)
        if not wesm.isCached() or self.forceUpdate:
            wesm.store()
        wem=WikidataEventManager(config=config)
        wem.fromCache(force=self.forceUpdate,getListOfDicts=wem.getLoDfromEndpoint)
        el=wem.getList()
        if self.debug:
            print(f"Found {len(el)} Wikidata scientific events")
        if not wem.isCached():
            wem.store()
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()