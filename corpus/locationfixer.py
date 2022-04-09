'''
Created on 2022-03-06

@author: wf
'''
from datetime import datetime
from corpus.utils.progress import Progress
from geograpy.locator import City
from lodstorage.tabulateCounter import TabulateCounter
from collections import Counter
from geograpy.locator import Locator
from corpus.location import LocationLookup
from corpus.lookup import CorpusLookup

class LocationFixer(object):
    '''
    fixer for locations - based on natural language location references
    such as 'Santa Fe, New Mexico, United States' the corresponding city, region
    and country information is looked up as a reference to wikiData and then
    added as the columns:
    city, region country and cityWikidataid, regionWikidataid and countryWikidataid
    '''
    
    def __init__(self):
        '''
        constructor
        '''
        # makes sure the geograpy3 data is available
        Locator.resetInstance()
        locator=Locator.getInstance()
        locator.downloadDB()
        self.locationLookup=LocationLookup()      
    
    def getCounter(self,events:list,propertyName:str):
        '''
        get a counter for the given event list and propertyName
        
        Args:
            events(list): a list of events to get counters for
            propertyName(str): the propertyname to count
            
        Returns:
            tuple(Counter,TabulateCounter): two counter representations
        '''
        counter=Counter()
        for event in events:
            if hasattr(event,propertyName):
                value=getattr(event,propertyName)
                if value is not None:
                    counter[value]+=1
        tabCounter=TabulateCounter(counter)
        return counter,tabCounter
    
    def timeStamp(self):
        '''
        get a timestamp with second precision
        
        Returns:
            str: an ISO-Date timestamp
        '''
        return datetime.utcnow().strftime('%Y-%m-%d_%H%M%S')
    
    def fixLocations4LookupIds(self,lookupIds,perCentLimit:float=60.0,logFileRoot="/tmp"):
        '''
        fix locations 4 the given lookup ids
        '''
        self.lookup=CorpusLookup(lookupIds=lookupIds)
        self.lookup.load(forceUpdate=False)
        for lookupId in lookupIds:
            dataSource=self.lookup.getDataSource(lookupId)
            eventManager=dataSource.eventManager
            show=True
            locationAttribute=dataSource.sourceConfig.locationAttribute
            limit=len(eventManager.getList())
            addLocationInfo=True
            showProgress=True
            logFile=None
            if logFileRoot is not None:
                timestamp=self.timeStamp()
                logFilePath=f"{logFileRoot}/{lookupId}-{timestamp}.log"
                logFile = open(logFilePath,'w')
            if lookupId=="dblp":
                eventManager.addLocations()
            self.fixLocations(eventManager, locationAttribute=locationAttribute, perCentLimit=perCentLimit,addLocationInfo=addLocationInfo, limit=limit, showProgress=showProgress,logFile=logFile)

    def fixLocations(self,eventManager,locationAttribute,perCentLimit=60.0,addLocationInfo=False,limit:int=100,showProgress=True,logFile=None):
        '''
        fix locations
        
        Args:
            eventManager: the eventmanager to use
            locationAttribute(str): the name of the location attribute
            addLocationInfo(bool): if True add the location information
            perCentLimit(float): percentage of Locations to cover (if less than 100% the fixing process will prematurely end at this limit)
        '''
        events=eventManager.events
        pCount,_pCountTab=self.getCounter(events,locationAttribute)
        eventsByLocation=eventManager.getLookup(locationAttribute,withDuplicates=True)
        count=len(pCount.items())
        total=sum(pCount.values())
        rsum=0
        problems=[]
        logHint=""
        if logFile:
            logHint=f"\nlogging to {logFile.name}"
        progress=Progress(progressSteps=1,expectedTotal=total,msg=f"Fixing {limit}/{total} locations for {eventManager.name} with perCentLimit {perCentLimit:.1f}% using location attribute {locationAttribute}{logHint}",showMemory=True)
        for i,locationTuple in enumerate(pCount.most_common(limit)):
            locationText,locationCount=locationTuple
            rsum+=locationCount
            percent=rsum/total*100
            city=None
            try:
                city=self.locationLookup.lookup(locationText,logFile=logFile)
            except Exception as ex:
                print(str(ex))
            if city is not None and isinstance(city,City):
                if showProgress:
                    progress.next()
                if logFile:
                    statsLine=f"{i:4d}/{count:4d}{rsum:6d}/{total:5d}({percent:4.1f}%)✅:{locationText}({locationCount})→{city} ({city.pop})"
                    print(statsLine,file=logFile,flush=True)
                events=eventsByLocation[locationText]
                # loop over all events and add location details
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
                if logFile:
                    print(f"{i:4d}/{count:4d}{rsum:6d}/{total:5d}({percent:4.1f}%)❌:{locationText}({locationCount})",file=logFile)
                problems.append(locationText)
            if percent>perCentLimit:
                break
        problemMsg=f"found {len(problems)} problems"
        progress.done()
        for i,problem in enumerate(problems):
            if logFile:
                print(f"{i:4d}:{problem}",file=logFile)        
        print(problemMsg,file=logFile,flush=True)      
        if addLocationInfo:
            eventManager.store()
            print(f"{len(eventManager.events)} events stored",file=logFile,flush=True)
        