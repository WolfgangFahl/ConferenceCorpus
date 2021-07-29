'''
Created on 2021-07-26

@author: wf
'''
import unittest
from tests.testSMW import TestSMW
from tests.testDblpXml import TestDblp
from corpus.lookup import CorpusLookup


class TestEventCorpus(unittest.TestCase):
    '''
    test the event corpus
    '''

    def setUp(self):
        self.debug=False
        pass


    def tearDown(self):
        pass
    
    def configureCorpusLookup(self,lookup:CorpusLookup):
        '''
        callback to configure the corpus lookup
        '''
        print("configureCorpusLookup callback called")
        dblpDataSource=lookup.getDataSource("dblp")
        dblp=TestDblp.getMockedDblp(debug=self.debug)
        dblpDataSource.eventManager.dblp=dblp
        dblpDataSource.eventSeriesManager.dblp=dblp
        
        orDataSource=lookup.getDataSource("or")
        wikiFileManager=TestSMW.getWikiFileManager()
        orDataSource.eventManager.wikiFileManager=wikiFileManager
        orDataSource.eventSeriesManager.wikiFileManager=wikiFileManager
        #wikiuser=TestSMW.getWikiUser()
        pass

    def testLookup(self):
        '''
        test the lookup
        '''
        lookup=CorpusLookup(configure=self.configureCorpusLookup)
        lookup.load()
        self.assertEqual(3,len(lookup.eventCorpus.eventDataSources))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()