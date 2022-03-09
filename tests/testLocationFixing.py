'''
Created on 2021-08-06

@author: wf
'''
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup

from collections import Counter
from corpus.event import EventStorage
from corpus.locationfixer import LocationFixer

from lodstorage.query import Query
import getpass
import os

class TestLocationFixing(DataSourceTest):
    '''
    test fixing Locations from different Datasources
    '''

    @classmethod
    def setUpClass(cls):
        super().setUpClass()      
        cls.locationFixer=LocationFixer()
        lookupIds=["crossref","confref","dblp","gnd","wikidata","wikicfp","orclone"]
        cls.lookup=CorpusLookup(lookupIds=lookupIds)
        cls.lookup.load(forceUpdate=False)
        
    def setUp(self):
        DataSourceTest.setUp(self)
        self.locationFixer=TestLocationFixing.locationFixer
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
            location=self.locationFixer.locationLookup.lookup(locationText)
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
    
    def testConfRefLocationFix(self):
        '''
        test fixing confref locations
        '''
        confrefDataSource=self.lookup.getDataSource("confref")
        limit=50 if self.inCI() else 200
        addLocationInfo=limit>=2000
        for event in confrefDataSource.eventManager.events:
            event.location=f"{event.city}, {event.country}"
        self.locationFixer.fixLocations(confrefDataSource.eventManager,locationAttribute="location",limit=limit,addLocationInfo=addLocationInfo)
        
    def testCrossRefLocationFix(self):
        '''
        test fixing CrossRef locations
        '''
        crossRefDataSource=self.lookup.getDataSource("crossref")
        # 40%   at  270 locations
        # 60%   at  692 locations
        # 79.7% at 2000 locations 
        limit=50 if self.inCI() else 200
        addLocationInfo=limit>=2000
        self.locationFixer.fixLocations(crossRefDataSource.eventManager,locationAttribute="location",limit=limit,addLocationInfo=addLocationInfo)
       
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
        addLocationInfo=limit>=1000
        self.locationFixer.fixLocations(wikicfpDataSource.eventManager, "locality",limit=limit,addLocationInfo=addLocationInfo) 
            
    def testDblpLocationFix(self):
        '''
        test dblp Location fixing
        '''
        dblpDataSource=self.lookup.getDataSource("dblp")
        # make sure locations are available
        dblpDataSource.eventManager.addLocations()
        #print(dblpEvent.location)
        # 48517 as of 2021-12-27
        limit=50 if self.inCI() else 1500
        addLocationInfo=limit>=1000
        self.locationFixer.fixLocations(dblpDataSource.eventManager, "location",limit=limit,addLocationInfo=addLocationInfo)
 
    def testGNDLocationFix(self):
        '''
        test fixing WikiCFP locations
        '''
        gndDataSource=self.lookup.getDataSource("gnd")
        # 87% at 3500 locations (  16 per location) - 2100 secs
        limit=50 if self.inCI() else 300
        addLocationInfo=limit>=1000
        self.locationFixer.fixLocations(gndDataSource.eventManager, "location",limit=limit,addLocationInfo=addLocationInfo) 
     
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
        addLocationInfo=limit>=1200
        self.locationFixer.fixLocations(orDataSource.eventManager, "location",limit=limit,addLocationInfo=addLocationInfo)
        
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
                pCount,pCountTab=self.locationFixer.getCounter(events,propertyName)
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
    DataSourceTest.main()