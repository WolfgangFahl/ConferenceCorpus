'''
Created on 2021-08-06

@author: wf
'''
import unittest
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup
from collections import Counter

class TestLocationFixing(DataSourceTest):
    '''
    test fixing Locations from different Datasources
    '''

    def setUp(self):
        DataSourceTest.setUp(self)
        pass


    def testCrossRef(self):
        '''
        test CrossRef locations
        '''
        lookup=CorpusLookup(lookupIds=["crossref"])
        lookup.load(forceUpdate=False)
        crossRefDataSource=lookup.getDataSource("crossref")
        events=crossRefDataSource.eventManager.events
        partCount=Counter()
        for event in events:
            #print(event.location)
            location=event.location
            if location is not None:
                parts=event.location.split(",")
                partCount[len(parts)]+=1
        print (partCount.most_common())
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()