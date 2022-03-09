'''
Created on 27.07.2021

@author: wf
'''
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup

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
    
    def testWikidata(self):
        '''
        test getting the wikiData Event Series
        '''
        self.checkDataSource(self.wikidataDataSource,4200,7500)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    DataSourceTest.main()