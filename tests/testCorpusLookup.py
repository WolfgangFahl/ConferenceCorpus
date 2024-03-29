'''
Created on 2021-07-26

@author: wf
'''
from tests.testSMW import TestSMW
from tests.testDblpXml import TestDblp
from corpus.lookup import CorpusLookup
from corpus.event import EventStorage
from tests.datasourcetoolbox import DataSourceTest
import json


class TestCorpusLookup(DataSourceTest):
    '''
    test the event corpus
    '''

    def setUp(self, debug=False, profile=True, **kwargs):
        DataSourceTest.setUp(self, debug=debug, profile=profile, **kwargs)
        pass
    
    def configureCorpusLookup(self,lookup:CorpusLookup):
        '''
        callback to configure the corpus lookup
        '''
        print("configureCorpusLookup callback called")
        dblpDataSource=lookup.getDataSource("dblp")
        dblpXml=TestDblp.getMockedDblp(debug=self.debug)
        dblpDataSource.eventManager.dblpXml=dblpXml
        dblpDataSource.eventSeriesManager.dblpXml=dblpXml
        
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
        self.assertGreaterEqual(len(lookup.eventCorpus.eventDataSources), 10)
                
    def testViewDDL(self):
        '''
        test the view DDL
        '''
        viewDDLs=EventStorage.getCommonViewDDLs()
        debug=self.debug
        #debug=True
        
        if debug:
            for viewDDL in viewDDLs.values():
                print(viewDDL)
        self.assertEqual(2,len(viewDDLs))
        for viewDDL in viewDDLs.values():
            self.assertTrue("CREATE VIEW" in viewDDL)
            
    def testGetDataSourceInfos(self):
        '''
        test getting the infos for the datasources
        '''
        lookup=CorpusLookup(configure=self.configureCorpusLookup)
        infos=lookup.getDataSourceInfos()
        # self.debug=True
        if self.debug:
            print(infos)
        
    def testDataSource4Table(self):
        '''
        test getting datasources by table name
        '''
        lookup=CorpusLookup(configure=self.configureCorpusLookup)
        dataSource=lookup.getDataSource4TableName("event_confref")
        if self.debug:
            print(f"{dataSource.name}")
        self.assertEqual("confref.org",dataSource.name)
        
    def testMultiQuery(self):
        '''
        test getting entries for a given query
        '''
        multiQuery="SELECT * FROM {event}"
        lookup=CorpusLookup(configure=self.configureCorpusLookup)
        variable=lookup.getMultiQueryVariable(multiQuery)
        debug=self.debug
        # debug=True
        if debug:
            print(f"found '{variable}' as the variable in '{multiQuery}'")
        self.assertEqual("event",variable)
        lookup.load()
        idQuery="""SELECT source,eventId FROM event WHERE acronym LIKE "%WEBIST%" ORDER BY year DESC"""
        dictOfLod=lookup.getDictOfLod4MultiQuery(multiQuery,idQuery)
        if debug:
            jsonStr=json.dumps(dictOfLod, sort_keys=True, indent=2,default=str)
            print(jsonStr)
        for dataSourceName in ["confref","dblp","wikicfp"]:
            self.assertTrue(dataSourceName in dictOfLod)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    DataSourceTest.main()