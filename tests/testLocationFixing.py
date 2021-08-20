'''
Created on 2021-08-06

@author: wf
'''
import unittest
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup
from corpus.location import LocationLookup
from collections import Counter
from geograpy.locator import City
from lodstorage.query import Query
from lodstorage.tabulateCounter import TabulateCounter
from corpus.event import EventStorage
import getpass
import os

class TestLocationFixing(DataSourceTest):
    '''
    test fixing Locations from different Datasources
    '''

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.locationLookup=LocationLookup()
        lookupIds=["crossref","confref","wikidata","wikicfp","or"]
        cls.lookup=CorpusLookup(lookupIds=lookupIds)
        cls.lookup.load(forceUpdate=False)
        
        
    def setUp(self):
        DataSourceTest.setUp(self)
        self.locationLookup=TestLocationFixing.locationLookup
        self.lookup
        pass
    
    @staticmethod
    def inCI():
        '''
        are we running in a Continuous Integration Environment?
        '''
        publicCI=getpass.getuser() in ["travis", "runner"] 
        jenkins= "JENKINS_HOME" in os.environ;
        return publicCI or jenkins
    
    def testQuery(self):
        sqlDB=EventStorage.getSqlDB()
        query=Query("SGK Example","select locality from event_wikicfp where seriesId=2693",lang='sql')
        localityRecords=sqlDB.query(query.query)
        query.documentQueryResult(localityRecords)
    
    def testLocationLookup(self):
        '''
        test the location lookup
        '''
        examples=[ 
            ("Beijing, China","Q956"),
            ("Washington, DC, USA","Q61"),
            ("Brno","Q14960")
        ] 
        failures=[]
        for locationText,expectedLocationId in examples:
            location=self.locationLookup.lookup(locationText)
            if not location.wikidataid == expectedLocationId:
                failures.append(locationText)
        if self.debug:
            print(f"locationLooup failed for {failures}")
        self.assertEqual(0,len(failures))
        

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

    def testCrossRefParts(self):
        '''
        test CrossRef locations
        '''
        crossRefDataSource=self.lookup.getDataSource("crossref")
        events=crossRefDataSource.eventManager.events
        partCount=Counter()
        for event in events:
            #print(event.location)
            location=event.location
            if location is not None:
                parts=event.location.split(",")
                partCount[len(parts)]+=1
        if self.debug:
            print (partCount.most_common())
        self.assertEqual(6,len(partCount))
        pass
    
    def testCrossRefLocationFix(self):
        '''
        test fixing CrossRef locations
        '''
        crossRefDataSource=self.lookup.getDataSource("crossref")
        events=crossRefDataSource.eventManager.events
        pCount,pCountTab=self.getCounter(events,"location")
        eventsByLocation=crossRefDataSource.eventManager.getLookup("location",withDuplicates=True)
        limit=500 
        #if TestLocationFixing.inCI() else 100
        total=sum(pCount.values())
        rsum=0
        for i,locationTuple in enumerate(pCount.most_common(limit)):
            locationText,locationCount=locationTuple
            rsum+=locationCount
            percent=rsum/total*100
            city=None
            try:
                city=self.locationLookup.lookup(locationText)
            except Exception as ex:
                print(str(ex))
            if city is not None and isinstance(city,City):
                print(f"{i:4d}{rsum:6d}/{total:5d}({percent:4.1f}%)✅:{locationText}({locationCount})→{city} ({city.population})")
            else:
                print(f"{i:4d}{rsum:6d}/{total:5d}({percent:4.1f}%)❌:{locationText}({locationCount})")
        
    
    def testStats(self):
        '''
        test ConfRef locations
        '''
        lookupIds=["crossref","confref","wikidata","wikicfp","or"]
        formats=["latex","grid","mediawiki","github"]
        show=self.debug
        show=True
        formats=["mediawiki"]
        
        for lookupId in lookupIds:
            dataSource=self.lookup.getDataSource(lookupId)
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