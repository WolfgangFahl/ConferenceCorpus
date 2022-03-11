'''
Created on 27.07.2021

@author: wf
'''
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup
from corpus.event import EventStorage

class TestWikiData(DataSourceTest):
    '''
    test wiki data access
    '''
        
    def setUp(self):
        DataSourceTest.setUp(self)
        self.lookup=CorpusLookup(lookupIds=["wikidata"])
        self.lookup.load(forceUpdate=False)
        self.wikidataDataSource=self.lookup.getDataSource("wikidata")
        pass
    
    def testQueryManager(self):
        '''
        
        test named query usage see
        https://github.com/WolfgangFahl/ConferenceCorpus/issues/45
        
        '''
        queryManager=EventStorage.getQueryManager(lang="sparql",name="wikidata")
        self.assertTrue(queryManager is not None)
        wikiDataEventsQuery=queryManager.queriesByName["Wikidata-Events"]
        debug= self.debug
        #debug=True
        if debug:
            print(wikiDataEventsQuery)
        self.assertEqual("sparql",wikiDataEventsQuery.lang)
        query=wikiDataEventsQuery.query
        self.assertTrue("?event wdt:P31 wd:Q2020153" in query)
        
    def testWikidata(self):
        '''
        test getting the wikiData Event Series
        '''
        self.checkDataSource(self.wikidataDataSource,4200,7500)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    DataSourceTest.main()