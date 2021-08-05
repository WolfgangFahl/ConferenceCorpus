'''
Created on 2021-07-31

@author: wf
'''
import unittest
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup

class TestStatistics(DataSourceTest):
    '''
    test statistics
    '''

    def setUp(self):
        DataSourceTest.setUp(self)
        pass


    def testStatistics(self):
        '''
        test statistics
        '''
        lookup=CorpusLookup()
        qm=lookup.getQueryManager()
        self.assertIsNotNone(qm)
        self.assertTrue(len(qm.queriesByName)>1)
        showMarkup=True
        for name,query in qm.queriesByName.items():
            listOfDicts=lookup.getLod4Query(query.query)
            if showMarkup:
                markup=query.asWikiMarkup(listOfDicts)
                print("== %s ==" % (name))
                print("=== query ===")
                print (query.asWikiSourceMarkup())
                print("=== result ===")
                print(markup)
        pass
    
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()