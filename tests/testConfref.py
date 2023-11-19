'''
Created on 2021-08-02

@author: wf
'''
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup

class TestConfRef(DataSourceTest):
    '''
    test getting events from Confref http://portal.confref.org
    as a data source
    '''

    def setUp(self):
        DataSourceTest.setUp(self)
        pass


    def testConfRef(self):
        '''
        test CrossRef as an event data source
        '''
        lookup=CorpusLookup(lookupIds=["confref"])
        lookup.load(forceUpdate=False)
        crossRefDataSource=lookup.getDataSource("confref")
        self.checkDataSource(crossRefDataSource,4800,37900)
        pass
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    DataSourceTest.main()