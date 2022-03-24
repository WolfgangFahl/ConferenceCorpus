'''
Created on 2020-09-15

@author: wf
'''
from corpus.eventcorpus import EventDataSource, EventDataSourceConfig
from corpus.event import EventStorage,EventSeriesManager, EventSeries, Event, EventManager
from lodstorage.storageconfig import StorageConfig
from datetime import datetime
import json
import re
from collections import Counter
from corpus.utils.textparse import Textparse

class GND(EventDataSource):
    '''
    manages event data from Gemeinsame Normdatei
    https://d-nb.info/standards/elementset/gnd
    '''
    debug=False
    host="confident.dbis.rwth-aachen.de"
    endpoint=f"https://{host}/jena/gnd/sparql"
    sourceConfig = EventDataSourceConfig(lookupId="gnd", name="GND", url='https://d-nb.info/standards/elementset/gnd', title='Gemeinsame Normdatei', tableSuffix="gnd",locationAttribute="location")
    
    def __init__(self,debug=False):
        '''
        constructor
        '''
        super().__init__(GndEventManager(), GndEventSeriesManager(), GND.sourceConfig)
        self.debug=debug
    
class ExtractStatistics:
    '''
    statistics 
    '''
    def __init__(self):
        self.counter=Counter()
        self.invalidTitles=[]
        self.invalidOrdinals=[]
        self.invalidYears=[]
        self.invalidDates=[]
        
    def dump(self):
        '''
        dump me
        '''
        timestamp=datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S')
        jsonfile = open(f"/tmp/extractstats_{timestamp}.json", "w")
        json.dump(self.__dict__, jsonfile, indent = 2)
        
    def addPartsLen(self,plen:int):
        self.counter[plen]+=1
        
    def addInvalidTitle(self,title):
        self.invalidTitles.append(title)
        self.counter["invalidTitle"]+=1
        
    def addInvalidOrdinal(self,ordinalStr):
        self.invalidOrdinals.append(ordinalStr)
        self.counter["invalidOrdinal"]+=1
       
    def addInvalidYear(self,yearStr): 
        self.invalidYears.append(yearStr)
        self.counter["invalidYear"]+=1
        
    def addInvalidDate(self,dateStr):
        self.invalidDates.append(dateStr)
        self.counter["invalidDate"]+=1
       
    
class GndTitleExtractor:
    
    def __init__(self,fulltitle:str,stats):
        '''
        constructor
        '''
        self.fulltitle=fulltitle
        self.stats=stats
        self._fields=["title","year","location","ordinal","organization"]
        
    def __str__(self):
        '''
        get my string representation
        '''
        text=""
        delim=""
        for field in self._fields:
            if hasattr(self, field):
                text+=f"{delim}{field}:{getattr(self,field)}" 
                delim="\n"
        return text
    
    def setOrganization(self,orgStr):
        self.organization=orgStr
    
    def setLocation(self,location):
        self.location=location.strip()
        
    def setOrdinal(self,ordinalStr):
        ordinalStr=ordinalStr.strip()
        m=re.match(r"^([0-9]+)\.?$",ordinalStr)
        if m:
            ordinal=int(m.group(1))
            self.ordinal=ordinal
            pass
        else:
            self.stats.addInvalidOrdinal(ordinalStr)
    
    def setYear(self,yearStr):
        '''
        set the year of the given event 
        
        Args:
            yearStr(str): the year string to analyze
        '''
        yearStr=yearStr.strip()
        if re.match(r"^[0-9]+$",yearStr):
            self.year=int(yearStr)
            return True
        else: 
            m=re.match(r"^([0-9]+)\s*\-\s*([0-9]+)$",yearStr)
            if m:
                self.year=int(m.group(1))
                self.stats.counter["yearRange"]+=1
                return True
            else:
                self.stats.addInvalidYear(yearStr)
                return False
     
    def titleExtract(self):
        '''
        extract meta data information from the given fulltitle of this gnd event
        
        Args:
            rawEvent(dict): the dict as queried
        '''
        regex=r"(.*?)\((.*?)\)"
        m=re.match(regex,self.fulltitle)
        stats=self.stats
        if m:
            self.title=m.group(1).strip()
            ordYearLocation=m.group(2)
            parts=ordYearLocation.split(":")
            plen=len(parts)
            stats.addPartsLen(plen)
            if plen==1:
                self.setYear(ordYearLocation)
            elif plen==2:
                self.setYear(parts[0])
                self.setLocation(parts[1])
            elif plen==3:
                self.setOrdinal(parts[0])
                self.setYear(parts[1])
                self.setLocation(parts[2])
            elif plen==4:
                self.setOrganization(parts[0])
                self.setOrdinal(parts[1])
                self.setYear(parts[2])
                self.setLocation(parts[3])
                pass
        else:
            stats.addInvalidTitle(self.fulltitle)
        
    def updateRawEvent(self,rawEvent:dict):
        '''
        update the given rawEvent with my values
        '''
        for field in self._fields:
            if hasattr(self, field):
                rawEvent[field]=getattr(self,field)
        
        
class GndEvent(Event):
    '''
    a scientific event derived from Gemeinsame Normdatei
    '''
    
    @classmethod
    def getSamples(cls):
        samples = [      
        ]
        return samples
    
            
    @classmethod
    def postProcessLodRecord(cls,rawEvent:dict):
        '''
        fix the given raw Event
        
        Args:
            rawEvent(dict): the raw event record to fix
        '''
      
class GndEventSeries(EventSeries):
    '''
    a scientific event series derived from Gemeinsame Normdatei
    '''
    
        
class GndEventManager(EventManager):
    '''
    manage WikiCFP derived scientific events
    '''

    def __init__(self, config:StorageConfig=None):
        '''
        Constructor
        '''
        self.source="gnd"
        self.endpoint=GND.endpoint
        self.queryManager=EventStorage.getQueryManager(lang="sparql",name="gnd")
        super().__init__(name="GndEvents", sourceConfig=GND.sourceConfig,clazz=GndEvent, config=config)
    
    def configure(self):
        '''
        configure me
        '''
        if not hasattr(self, "getListOfDicts"):
            self.getListOfDicts=self.getLoDfromEndpoint
        
    def postProcessEntityList(self,debug:bool=False):
        '''
        postProcess Events
        '''
        stats=ExtractStatistics()
        for event in self.events:
            titleExtractor=GndTitleExtractor(getattr(event, "fulltitle", ""),stats)
            titleExtractor.titleExtract()
            titleExtractor.updateRawEvent(event.__dict__)
            dateRange=(Textparse.getDateRange(event.date))
            if (len(dateRange)==0 and event.date is not None):
                stats.addInvalidDate(event.date)
            else:
                Textparse.setDateRange(event, dateRange)
        print(stats.counter.most_common())
        if debug:
            stats.dump()
        return stats
    
    def getSparqlQuery(self):
        '''
        get  the SPARQL query for this event manager
        '''
        gndquery=self.queryManager.queriesByName["GND-Events"]
        sparql=gndquery.query
        return sparql


class GndEventSeriesManager(EventSeriesManager):
    '''
    manage GND derived scientific conference series
    '''

    def __init__(self, config:StorageConfig=None):
        '''
        Constructor
        '''
        self.source="gnd"
        self.endpoint=GND.endpoint
        super().__init__(name="GndEventSeries", sourceConfig=GND.sourceConfig, clazz=GndEventSeries, config=config)

    def configure(self):
        '''
        configure me
        '''
        if not hasattr(self, "getListOfDicts"):
            #self.getListOfDicts=self.getLoDfromEndpoint  
            self.getListOfDicts=self.getDummyLoD
            
    def getDummyLoD(self):
        lod=[
            {
                "seriesId":"0",
                "title":""
            }
        ]
        return lod
        
    def getSparqlQuery(self):
        '''
        get  the SPARQL query for this event series manager
        '''
        sparql="""SELECT ?s ?p ?o 
WHERE {
  VALUES (?s) { ("subject") }
  VALUES (?p) { ("predicate") }
  VALUES (?o) { ("object") }
}
        """
        return sparql
        