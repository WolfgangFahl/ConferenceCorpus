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
        #showMarkup=False
        showMarkup=True
        failCount=0
        for name,query in qm.queriesByName.items():
            try:
                listOfDicts=lookup.getLod4Query(query.query)
                qdoc=query.documentQueryResult(listOfDicts)
                if showMarkup:
                    print(qdoc)
            except Exception as ex:
                print (f"query: {query.query} failed:\n{ex}")
                failCount+=1
        self.assertEqual(0,failCount)
        pass
    
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()