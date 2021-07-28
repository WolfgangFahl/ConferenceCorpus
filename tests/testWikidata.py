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
        pass


    def tearDown(self):
        pass


    def testWikidata(self):
        '''
        test getting the wikiData Event Series
        '''
        config=StorageConfig.getSQL()
        wesm=WikidataEventSeriesManager(config=config)
        wesm.fromEndpoint()
        esl=wesm.getList()
        if self.debug:
            print(f"Found {len(esl)} Wikidata event Series")
        self.assertTrue(len(esl)>4200)
        if not wesm.isCached():
            wesm.store()
        wem=WikidataEventManager(config=config)
        wem.fromEndpoint()
        el=wem.getList()
        if self.debug:
            print(f"Found {len(el)} Wikidata scientific events")
        if not wem.isCached():
            wem.store()
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()