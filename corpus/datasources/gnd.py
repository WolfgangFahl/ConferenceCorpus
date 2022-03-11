'''
Created on 2020-09-15

@author: wf
'''
from corpus.eventcorpus import EventDataSource, EventDataSourceConfig
from corpus.event import EventStorage,EventSeriesManager, EventSeries, Event, EventManager
from lodstorage.storageconfig import StorageConfig
import re

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
        
class GndEvent(Event):
    '''
    a scientific event derived from Gemeinsame Normdatei
    '''
    @classmethod
    def getSamples(cls):
        samples = [      
        ]
        return samples
    
    def setOrganization(self,orgStr):
        self.organization=orgStr
    
    def setLocation(self,location):
        self.location=location
        
    def setOrdinal(self,ordinalStr,counter):
        ordinalStr=ordinalStr.strip()
        m=re.match(r"^([0-9]+)\.?$",ordinalStr)
        if m:
            ordinal=int(m.group(1))
            self.ordinal=ordinal
            pass
        else:
            if GND.debug:
                print(f"ordinal?:{ordinalStr}")
            counter["invalidOrdinal"]+=1
    
    def setYear(self,yearStr,counter):
        '''
        set the year of the given event
        '''
        yearStr=yearStr.strip()
        if re.match(r"^[0-9]+$",yearStr):
            self.year=int(yearStr)
            return True
        else: 
            m=re.match(r"^([0-9]+)\s*\-\s*([0-9]+)$",yearStr)
            if m:
                self.year=int(m.group(1))
                counter["yearRange"]+=1
                return True
            else:
                if GND.debug:
                    print(f"year?:{yearStr}")
                counter["invalidYear"]+=1
                return False
        
    def titleExtract(self,counter):
        '''
        extract meta data information from the title of this gnd event
        '''
        regex=r"(.*?)\((.*?)\)"
        m=re.match(regex,self.title)
        if m:
            self.title=m.group(1)
            ordYearLocation=m.group(2)
            parts=ordYearLocation.split(":")
            plen=len(parts)
            counter[plen]+=1
            if plen==1:
                self.setYear(ordYearLocation,counter)
            elif plen==2:
                self.setYear(parts[0],counter)
                self.setLocation(parts[1])
            elif plen==3:
                self.setOrdinal(parts[0],counter)
                self.setYear(parts[1],counter)
                self.setLocation(parts[2])
            elif plen==4:
                self.setOrganization(parts[0])
                self.setOrdinal(parts[1],counter)
                self.setYear(parts[2],counter)
                self.setLocation(parts[3])
                pass
        else:
            #print(event.title)
            counter["invalid"]+=1
      
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
        self.queryManager=EventStorage.getQueryManager(lang="sparql",name="wikidata")
        super().__init__(name="GndEvents", sourceConfig=GND.sourceConfig,clazz=GndEvent, config=config)
    
    def configure(self):
        '''
        configure me
        '''
        if not hasattr(self, "getListOfDicts"):
            self.getListOfDicts=self.getLoDfromEndpoint
    
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
        