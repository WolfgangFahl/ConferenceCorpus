'''
Created on 2022-03-4

@author: wf
'''
import unittest
from corpus.trulytabular import TrulyTabular
from tabulate import tabulate

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
                
    def documentQuery(self,tt,query,show=True,formats=["mediawiki"]):
        '''
        document the given query for the given TrueTabular instance
        '''
        qlod=tt.sparql.queryAsListOfDicts(query.query)
        for tablefmt in formats:
            tryItUrl="https://query.wikidata.org/"
            doc=query.documentQueryResult(qlod, tablefmt=tablefmt,tryItUrl=tryItUrl,floatfmt=".0f")
            docstr=doc.asText()
            if show:
                print (docstr)
                
    def testGetPropertiesByLabel(self):
        '''
        try getting properties by label
        '''
        debug=self.debug
        debug=True
        tt=TrulyTabular("Q2020153",["title","country","location"])
        if debug:
            print (tt.properties)

    def testTrulyTabularTables(self):
        '''
        test Truly Tabular for academic conferences
        '''
        debug=self.debug
        debug=True
        show=False
        showStats=["mediawiki","github","latex"]
        tables=[ 
            {
               "qid":"Q5", # human
               "where": "?item wdt:P106 wd:Q82594.", # computer scientist only
               "propertyLabels": ["sex or gender","date of birth","ORCID iD","GND ID","DBLP author ID","Google Scholar author ID"],
               "expected": 10  
            },
            {
               "qid": "Q2020153",# academic conference
               "propertyLabels":["title","country","location","short name","start time",
                "end time","part of the series","official website","described at URL",
                "WikiCFP event ID","GND ID","VIAF ID","main subject","language used",
                "is proceedings from"
               ],
               "expected": 7500
            },
            {
                "qid": "Q47258130", # scientific conference series
                "propertyLabels":["title","short name","inception","official website","DBLP venue ID","GND ID",
                    "Microsoft Academic ID","Freebase ID","WikiCFP conference series ID",
                    "Publons journals/conferences ID","ACM conference ID"],
                "expected": 4200
            }
        ]
        errors=0
        for table in tables:
            # academic conference
            where=None
            if "where" in table:
                where=table["where"]
            tt=TrulyTabular(table["qid"],table["propertyLabels"],where=where,debug=debug)
            if "is proceedings from" in tt.properties:
                tt.properties["is proceedings from"].reverse=True
            count=tt.count()
            if (debug):
                print(count)
            self.assertTrue(count>table["expected"])
            stats=tt.getPropertyStatics()
            stats = sorted(stats, key=lambda row: row['total%']) 
            for tablefmt in showStats:
                print(tabulate(stats,headers="keys",tablefmt=tablefmt))
            if show:
                for wdProperty in tt.properties.values():
                    for asFrequency in [True,False]:
                        query=tt.noneTabularQuery(wdProperty,asFrequency=asFrequency)
                        try:
                            self.documentQuery(tt, query)
                        except Exception as ex:
                            print(f"query for {wdProperty} failed\n{str(ex)}")
                            errors+=1
                self.assertEqual(0,errors)
            
                
    def testMostFrequentIdentifiers(self):
        '''
        test getting the most frequent identifiers for some Wikidata Items
        '''
        show=True
        for qid in ["Q2020153","Q47258130","Q1143604"]:
            tt=TrulyTabular(qid)
            query=tt.mostFrequentIdentifiersQuery()
            self.documentQuery(tt, query,formats=["github"],show=show)
           


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()