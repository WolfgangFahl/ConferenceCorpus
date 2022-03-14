'''
Created on 2022-03-4

@author: wf
'''
import unittest
from corpus.trulytabular import TrulyTabular


class TestTrulyTabular(unittest.TestCase):
    '''
    test Truly tabular analysis
    '''


    def setUp(self):
        self.debug=False
        pass


    def tearDown(self):
        pass

    def testGetFirst(self):
        '''
        test the get First helper function
        '''
        tt=TrulyTabular("Q2020153")
        testcases=[
            { 
                "qlod":[{"name":"firstname"}],
                "expected": "firstname"
            },
            {
                "qlod":[],
                "expected": None
            },
            {
                "qlod":[{"name":"firstname"},{"name":"second name"}],
                "expected": None
            }
        ]
        for testcase in testcases:
            qLod=testcase["qlod"]
            expected=testcase["expected"]
            try:
                value=tt.getFirst(qLod,"name")
                self.assertEqual(expected,value)
            except Exception as ex:
                if self.debug:
                    print(str(ex))
                self.assertIsNone(expected)

    def testAcademicConference(self):
        '''
        test Truly Tabular for academic conferences
        '''
        debug=True
        tt=TrulyTabular("Q2020153",debug=debug)
        count=tt.count()
        self.assertTrue(count>7500)
        if (debug):
            print(count)
        for propertyId,propertyName,reverse in [
            ("P276", "location",False),
            ("P4745","proceedings",True)
        ]:
            qlod=tt.noneTabular(propertyId,propertyName,reverse)
            if (debug):
                print (qlod)
                
        if (debug):
            query=tt.mostFrequentIdentifiersQuery()
            
        pass
    
    def testMostFrequentIdentifiers(self):
        show=True
        for qid in ["Q2020153","Q47258130","Q1143604"]:
            tt=TrulyTabular(qid)
            query=tt.mostFrequentIdentifiersQuery()
            qlod=tt.sparql.queryAsListOfDicts(query.query)
            for tablefmt in ["mediawiki"]: # ,"github","latex"]:
                doc=query.documentQueryResult(qlod, tablefmt=tablefmt,floatfmt=".0f")
                docstr=doc.asText()
                if show:
                    print (docstr)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()