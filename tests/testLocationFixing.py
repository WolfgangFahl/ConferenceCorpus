'''
Created on 2021-08-06

@author: wf
'''
import unittest
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup
from collections import Counter
from lodstorage.tabulateCounter import TabulateCounter

class TestLocationFixing(DataSourceTest):
    '''
    test fixing Locations from different Datasources
    '''

    def setUp(self):
        DataSourceTest.setUp(self)
        pass

    def getCounter(self,events:list,propertyName:str):
        '''
        get a counter for the given propertyName
        '''
        counter=Counter()
        for event in events:
            if hasattr(event,propertyName):
                value=getattr(event,propertyName)
                if value is not None:
                    counter[value]+=1
        tabCounter=TabulateCounter(counter)
        return counter,tabCounter

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
    
    def testStats(self):
        '''
        test ConfRef locations
        '''
        lookupIds=["crossref","confref","wikidata","wikicfp","or"]
        formats=["latex","grid","mediawiki","github"]
        lookup=CorpusLookup(lookupIds=lookupIds)
        lookup.load(forceUpdate=False)
        show=self.debug
        show=True
        formats=["mediawiki"]
        
        for lookupId in lookupIds:
            dataSource=lookup.getDataSource(lookupId)
            events=dataSource.eventManager.events
            for propertyName in ["locality","location","country","region","city"]:
                pCount,pCountTab=self.getCounter(events,propertyName)
                if len(pCount)>0:
                    if show:
                        print(f"=={dataSource.sourceConfig.title}:{propertyName}==")
                        for fmt in formats:
                            print(pCountTab.mostCommonTable(tablefmt=fmt,limit=20))
      
    #     found=0
    #    for ce in confRefEvents:
    #       if ce.country in wcountryCount:
    #          #print(f"{ce.eventId}-{ce.country}")
    #          found+=1
    #  print(found)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()