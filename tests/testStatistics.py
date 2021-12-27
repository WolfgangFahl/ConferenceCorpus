'''
Created on 2021-07-31

@author: wf
'''
import unittest
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup
from lodstorage.query import Query
import copy

class TestStatistics(DataSourceTest):
    '''
    test statistics
    '''
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.lookup=CorpusLookup()
       

    def setUp(self):
        DataSourceTest.setUp(self)
        self.lookup=TestStatistics.lookup
        
        pass
    
    def testIssue255(self):
        '''
        '''
        show=False
        lookup=self.lookup
        sqlQuery="""select url,endDate-startdate+1 as duration from 
event_orclone
where endDate is not Null and startDate is not Null
and duration<0 or  duration>7
order by duration"""
        query=Query(name="issue #255",query=sqlQuery,lang='sql')
        qlod=lookup.getLod4Query(query.query)
        prefix="https://confident.dbis.rwth-aachen.de/or/index.php?title="
        for tablefmt in ["mediawiki","github","latex"]:
            lod=copy.deepcopy(qlod)
            query.prefixToLink(lod, prefix, tablefmt)
            qdoc=query.documentQueryResult(lod,tablefmt=tablefmt)
            if show:
                print(qdoc)

    def testStatistics(self):
        '''
        test statistics
        '''
        lookup=self.lookup;
        qm=self.lookup.getQueryManager()
        self.assertIsNotNone(qm)
        self.assertTrue(len(qm.queriesByName)>1)
        showMarkup=False
        #showMarkup=True
        failCount=0
        for _name,query in qm.queriesByName.items():
            try:
                qlod=lookup.getLod4Query(query.query)
                for tablefmt in ["mediawiki","github","latex"]:
                    qdoc=query.documentQueryResult(qlod,tablefmt=tablefmt)
                    if showMarkup:
                        print(qdoc)
            except Exception as ex:
                print (f"query: {query.query} failed:\n{ex}")
                failCount+=1
        self.assertTrue(failCount<=3)
        pass
    
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()