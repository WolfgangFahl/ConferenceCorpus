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
    fixer for locations
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
    
    def timeStamp(self):
        '''
        get a timestamp with second precision
        '''
        return datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S')
    
    def fixLocations4LookupId(self,lookupIds,logFileRoot="/tmp"):
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
            self.fixLocations(eventManager, locationAttribute, addLocationInfo, limit, showProgress=showProgress,logFile=logFile)

    def fixLocations(self,eventManager,locationAttribute,addLocationInfo=False,limit=100,showProgress=True,logFile=None):
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
        progress=Progress(progressSteps=1,expectedTotal=total,msg=f"Fixing {limit}/{total} locations for {eventManager.name} using location attribute {locationAttribute}",showMemory=True)
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
                    print(f"{i:4d}/{count:4d}{rsum:6d}/{total:5d}({percent:4.1f}%)✅:{locationText}({locationCount})→{city} ({city.pop})",file=logFile)
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
                if logFile:
                    print(f"{i:4d}/{count:4d}{rsum:6d}/{total:5d}({percent:4.1f}%)❌:{locationText}({locationCount})",file=logFile)
                problems.append(locationText)
        problemMsg=f"found {len(problems)} problems"
        progress.done()
        for i,problem in enumerate(problems):
            if logFile:
                print(f"{i:4d}:{problem}",file=logFile)        
        print(problemMsg,file=logFile)      
        if addLocationInfo:
            eventManager.store()   
        