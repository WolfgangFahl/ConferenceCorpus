'''
Created on 2021-07-26

@author: wf
'''
import unittest
from tests.testSMW import TestSMW
from tests.testDblpXml import TestDblp
from corpus.lookup import CorpusLookup
from corpus.event import EventStorage

class TestCorpusLookup(unittest.TestCase):
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
        
        for lookupId in ["or","orclone"]:
            orDataSource=lookup.getDataSource(lookupId)
            wikiFileManager=TestSMW.getWikiFileManager(wikiId=lookupId)
            orDataSource.eventManager.wikiFileManager=wikiFileManager
            orDataSource.eventSeriesManager.wikiFileManager=wikiFileManager
            orDataSource=lookup.getDataSource(f'{lookupId}-backup')
            wikiUser=TestSMW.getSMW_WikiUser(lookupId)
            orDataSource.eventManager.wikiUser=wikiUser
            orDataSource.eventSeriesManager.wikiUser=wikiUser
        
        #wikiuser=TestSMW.getWikiUser()
        pass

    def testLookup(self):
        '''
        test the lookup
        '''
        lookup=CorpusLookup(configure=self.configureCorpusLookup)
        lookup.load()
        self.assertEqual(7,len(lookup.eventCorpus.eventDataSources))
        
    def testGetPlantUmlDiagram(self):
        '''
        test creating a plantuml diagram of the tables involved in the lookup
        '''
        lookup=CorpusLookup(configure=self.configureCorpusLookup)
        lookup.load()
        storageTableList=EventStorage.getTableList()
        self.assertEqual(14,len(storageTableList))
        for baseEntity in ["Event","EventSeries"]:
            plantUml=lookup.asPlantUml(baseEntity)
            debug=self.debug
            debug=True
            if debug:
                print(plantUml)
            self.assertTrue(f"{baseEntity} <|-- dblp_{baseEntity}" in plantUml)
            self.assertTrue(f"class {baseEntity} " in plantUml)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()