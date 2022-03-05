'''
Created on 2021-08-06

@author: wf
'''
import unittest
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup
from corpus.location import LocationLookup
from collections import Counter
from geograpy.locator import City,Locator
from lodstorage.query import Query
from lodstorage.tabulateCounter import TabulateCounter
from corpus.event import EventStorage
from corpus.utils.progress import Progress
import getpass
import os

class TestLocationFixing(DataSourceTest):
    '''
    test fixing Locations from different Datasources
    '''

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # makes sure the geograpy3 data is available
        Locator.resetInstance()
        locator=Locator.getInstance()
        locator.downloadDB()
        
        cls.locationLookup=LocationLookup()
        lookupIds=["crossref","confref","dblp","gnd","wikidata","wikicfp","orclone"]
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
        '''
        test helpful queries for example selection
        '''
        sqlDB=EventStorage.getSqlDB()
        queries=[
            ("wikicfp locality histogramm","""select count(*),seriesId,locality
from event_wikicfp
where seriesId is not null
group by seriesId,locality
order by 1 desc
limit 20"""),
            ("SGK Example","select locality from event_wikicfp where seriesId=2693")
]
        for title,queryString in queries:
            query=Query(title,queryString,lang='sql')
            localityRecords=sqlDB.query(query.query)
            dqr=query.documentQueryResult(localityRecords)
            if self.debug:
                print(dqr)
    
    def testLocationLookup(self):
        '''
        test the location lookup
        '''
        examples=[ 
            ("Westonaria,Gauteng,South Africa","Q2671197"),
            ("Beijing, China","Q956"),
            ("Washington, DC, USA","Q61"),
            ("Brno","Q14960"),
            
        ] 
        failures=[]
        show=self.debug
        for locationText,expectedLocationId in examples:
            location=self.locationLookup.lookup(locationText)
            if show:
                print(location)
            if not location.wikidataid == expectedLocationId:
                failures.append(locationText)
        if self.debug:
            print(f"locationLooup failed for {failures}")
        self.assertEqual(0,len(failures))

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
    
    def fixLocations(self,eventManager,locationAttribute,addLocationInfo=False,limit=100,show=True):
        '''
        fix locations
        
        Args:
            eventManager: the eventmanager to use
            locationAttribute(str): the name of the location attribute
            addLocationInfo(bool): if True add the location information
        '''
        events=eventManager.events
        pCount,_pCountTab=self.getCounter(events,locationAttribute)
        eventsByLocation=eventManager.getLookup(locationAttribute,withDuplicates=True)
        count=len(pCount.items())
        total=sum(pCount.values())
        rsum=0
        problems=[]
        progress=Progress(100)
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
                if show:
                    if self.inCI():
                        progress.next()
                    else:
                        print(f"{i:4d}/{count:4d}{rsum:6d}/{total:5d}({percent:4.1f}%)✅:{locationText}({locationCount})→{city} ({city.pop})")
                events=eventsByLocation[locationText]
                # loop over all events
                for event in events:
                    event.city=city.name
                    event.cityWikidataid=city.wikidataid
                    
                    event.region=city.region.name
                    event.regionIso=city.region.iso
                    event.regionWikidataid=city.region.wikidataid
                    event.country=city.country.name
                    event.countryIso=city.country.iso
                    event.countryWikidataid=city.country.wikidataid
            else:
                if show:
                    print(f"{i:4d}/{count:4d}{rsum:6d}/{total:5d}({percent:4.1f}%)❌:{locationText}({locationCount})")
                problems.append(locationText)
        for i,problem in enumerate(problems):
            if show:
                print(f"{i:4d}:{problem}")        
        print(f"found {len(problems)} problems")      
        if addLocationInfo:
            eventManager.store()       
    
    def testConfRefLocationFix(self):
        '''
        test fixing confref locations
        '''
        confrefDataSource=self.lookup.getDataSource("confref")
        limit=50 if self.inCI() else 200
        show=not self.inCI()
        addLocationInfo=limit>=2000
        for event in confrefDataSource.eventManager.events:
            event.location=f"{event.city}, {event.country}"
        self.fixLocations(confrefDataSource.eventManager,locationAttribute="location",limit=limit,show=show,addLocationInfo=addLocationInfo)
        
    def testCrossRefLocationFix(self):
        '''
        test fixing CrossRef locations
        '''
        crossRefDataSource=self.lookup.getDataSource("crossref")
        # 40%   at  270 locations
        # 60%   at  692 locations
        # 79.7% at 2000 locations 
        limit=50 if self.inCI() else 200
        show=not self.inCI()
        addLocationInfo=limit>=2000
        self.fixLocations(crossRefDataSource.eventManager,locationAttribute="location",limit=limit,show=show,addLocationInfo=addLocationInfo)
       
    def testWikiCFPLocationFix(self):
        '''
        test fixing WikiCFP locations
        '''
        wikicfpDataSource=self.lookup.getDataSource("wikicfp")
        # 20% at   35 locations (220 per location)
        # 40% at  172 locations ( 67 per location)
        # 60% at  634 locations ( 19 per location)
        # 80% at 3144 locations (  3 per location) - 1166 secs
        limit=50 if self.inCI() else 175  
        show=not self.inCI()
        addLocationInfo=limit>=1000
        self.fixLocations(wikicfpDataSource.eventManager, "locality",limit=limit,show=show,addLocationInfo=addLocationInfo) 
            
    def testDblpLocationFix(self):
        '''
        test dblp Location fixing
        '''
        dblpDataSource=self.lookup.getDataSource("dblp")
        for dblpEvent in dblpDataSource.eventManager.events:
            title=dblpEvent.title
            if title is not None:
                parts=title.split(",")
                if len(parts)>3:
                    dblpEvent.location=f"{parts[2].strip()}, {parts[3].strip()}"
                    #print(dblpEvent.location)
        # 48517 as of 2021-12-27
        limit=50 if self.inCI() else 1500
        show=not self.inCI()
        addLocationInfo=limit>=1000
        self.fixLocations(dblpDataSource.eventManager, "location",limit=limit,show=show,addLocationInfo=addLocationInfo)
 
    def testGNDLocationFix(self):
        '''
        test fixing WikiCFP locations
        '''
        gndDataSource=self.lookup.getDataSource("gnd")
        # 87% at 3500 locations (  16 per location) - 2100 secs
        limit=50 if self.inCI() else 300
        show=not self.inCI()
        addLocationInfo=limit>=1000
        self.fixLocations(gndDataSource.eventManager, "location",limit=limit,show=show,addLocationInfo=addLocationInfo) 
     
    def testORLocationFix(self):
        '''
        test OpenResearch Location Fixing
        '''
        orDataSource=self.lookup.getDataSource("orclone")
        for orEvent in orDataSource.eventManager.events:
            loc=""
            delim=""
            if orEvent.city:
                city=orEvent.city.replace("Category:","")
                loc=f"{city}"
                delim=", "
            if orEvent.region:
                region=orEvent.region.replace("Category:","")
                loc=f"{loc}{delim}{region}"
                delim=", "    
            if orEvent.country:
                country=orEvent.country.replace("Category:","")
                loc=f"{loc}{delim}{country}"
            orEvent.location=loc
            pass
        # 1500 -> > 90%
        limit=50 if self.inCI() else 200
        show=not self.inCI()
        addLocationInfo=limit>=1200
        self.fixLocations(orDataSource.eventManager, "location",limit=limit,show=show,addLocationInfo=addLocationInfo)
        
        
    def testStats(self):
        '''
        test ConfRef locations
        '''
        lookupIds=["crossref","confref","wikidata","wikicfp","orclone"]
        formats=["latex","grid","mediawiki","github"]
        show=self.debug
        #show=True
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