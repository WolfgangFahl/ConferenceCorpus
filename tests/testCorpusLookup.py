'''
Created on 2021-07-26

@author: wf
'''
import unittest
from tests.testSMW import TestSMW
from tests.testDblpXml import TestDblp
from corpus.lookup import CorpusLookup
from corpus.event import EventStorage
from tests.datasourcetoolbox import DataSourceTest

class TestCorpusLookup(DataSourceTest):
    '''
    test the event corpus
    '''

    def setUp(self):
        DataSourceTest.setUp(self)
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
            orDataSource=lookup.getDataSource(f'{lookupId}-backup')
            wikiFileManager=TestSMW.getWikiFileManager(wikiId=lookupId)
            orDataSource.eventManager.wikiFileManager=wikiFileManager
            orDataSource.eventSeriesManager.wikiFileManager=wikiFileManager
            orDataSource=lookup.getDataSource(lookupId)
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
        self.assertEqual(9,len(lookup.eventCorpus.eventDataSources))
        
    def testViewDDL(self):
        '''
        test the view DDL
        '''
        viewDDL=EventStorage.getCommonViewDDL()
        if self.debug:
            print(viewDDL)
        self.assertTrue("CREATE VIEW" in viewDDL)
        
    def testDataSource4Table(self):
        '''
        test getting datasources by table name
        '''
        lookup=CorpusLookup(configure=self.configureCorpusLookup)
        dataSource=lookup.getDataSource4TableName("confref_Event")
        if self.debug:
            print (f"{dataSource.name}")
        self.assertEqual("confref.org",dataSource.name)
        
    def testGetPlantUmlDiagram(self):
        '''
        test creating a plantuml diagram of the tables involved in the lookup
        '''
        lookup=CorpusLookup(configure=self.configureCorpusLookup)
        lookup.load()
        storageTableList=EventStorage.getTableList()
        self.assertEqual(18,len(storageTableList))
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