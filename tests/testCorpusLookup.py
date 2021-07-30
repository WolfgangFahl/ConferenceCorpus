'''
Created on 2021-07-26

@author: wf
'''
import unittest
from tests.testSMW import TestSMW
from tests.testDblpXml import TestDblp
from corpus.lookup import CorpusLookup
from lodstorage.uml import UML
from datetime import datetime

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
        self.assertEqual(6,len(lookup.eventCorpus.eventDataSources))
        
    def testGetPlantUmlDiagram(self):
        '''
        test creating a plantuml diagram of the tables involved in the lookup
        '''
        lookup=CorpusLookup(configure=self.configureCorpusLookup)
        lookup.load()
        tableMap=lookup.getTableMap()
        print (tableMap)
        eventTableList=[]
        for table in tableMap.values():
            eventTableList.append(table)
        self.assertEqual(12,len(tableMap))
        schemaManager=None
        uml=UML()
        now=datetime.now()
        nowYMD=now.strftime("%Y-%m-%d")
        title="""ConfIDent  Entities
%s
[[https://projects.tib.eu/en/confident/ © 2019-2021 ConfIDent project]]
see also [[http://ptp.bitplan.com/settings Proceedings Title Parser]]
""" %nowYMD
        plantUml=uml.mergeSchema(schemaManager,eventTableList,title=title,packageName='DataSources',generalizeTo="Event")
        print(plantUml)
        self.assertTrue("Event <|-- Event_confref" in plantUml)
        self.assertTrue("class Event " in plantUml)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()