'''
Created on 2020-09-15

@author: wf
'''
from corpus.eventcorpus import EventDataSource, EventDataSourceConfig
from corpus.event import EventStorage,EventSeriesManager, EventSeries, Event, EventManager
from lodstorage.storageconfig import StorageConfig
import re
import datetime

class GND(EventDataSource):
    '''
    manages event data from Gemeinsame Normdatei
    https://d-nb.info/standards/elementset/gnd
    '''
    debug=False
    host="confident.dbis.rwth-aachen.de"
    endpoint=f"https://{host}/jena/gnd/sparql"
    limit=1000000
    sourceConfig = EventDataSourceConfig(lookupId="gnd", name="GND", url='https://d-nb.info/standards/elementset/gnd', title='Gemeinsame Normdatei', tableSuffix="gnd")
    
    def __init__(self,debug=False):
        '''
        constructor
        '''
        super().__init__(GndEventManager(), GndEventSeriesManager(), GND.sourceConfig)
        self.debug=debug
        
    @staticmethod
    def strToDate(dateStr,debug:bool=False):
        '''
        convert the given string to a date
        
        Args:
            dateStr(str): the date string to convert
            debug(bool): if True show debug information
            
        Return:
            Date: - the converted data but None if there is a ValueError on conversion
        '''
        result=None
        try:
            result=datetime.datetime.strptime(
                        dateStr, "%d.%m.%Y").date()
        except ValueError as ve:
            # TODO year might be ok but not garbage such as
            if debug:
                print(f"{dateStr}:{str(ve)}")
            pass
        return result
        
    @staticmethod
    def getDateRange(date):
        '''
        given a GND date string create a date range
        
        Args:
            date(str): the date string to analyze
            
        Returns:
            dict: containing year, startDate, endDate
        examples:
        2018-2019
        08.01.2019-11.01.2019
        2019
        '''
        result={}
        if date is not None:
            startDate=None
            endDate=None
            yearPattern="[12][0-9]{3}"
            datePattern="[0-9]{2}[.][0-9]{2}[.]"+yearPattern
            yearOnly=re.search(r"^("+yearPattern+")[-]?("+yearPattern+")?$",date)
            if yearOnly:
                result['year']=int(yearOnly.group(1))
            else:
                fromOnly=re.search(r"^("+datePattern+")[-]?$",date)
                if fromOnly:
                    startDate=GND.strToDate(fromOnly.group(1))
                else:
                    fromTo=re.search(r"^("+datePattern+")[-]("+datePattern+")$",date)
                    if fromTo:
                        startDate=GND.strToDate(fromTo.group(1))
                        endDate=GND.strToDate(fromTo.group(2))
            if startDate:
                result['startDate']=startDate
            if endDate:
                result['endDate']=endDate
        if 'startDate' in result:
                result['year']=result['startDate'].year
        return result

        
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
        sparql="""# performance optimized query of GND event details
# with aggregated properties as single, count and | separated list column
# WF 2021-12-05
PREFIX gndi:  <https://d-nb.info/gnd>
PREFIX gnd:  <https://d-nb.info/standards/elementset/gnd#>
PREFIX gndo: <https://d-nb.info/standards/vocab/gnd/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX dc: <http://purl.org/dc/terms/>
PREFIX wdrs: <http://www.w3.org/2007/05/powder-s#>

SELECT  
   ?event 
   ?eventId  
   (MIN(?eventTitle) as ?title)

   (COUNT (DISTINCT ?eventDate) as ?dateCount)
   (MIN(?eventDate) as ?date)

   (MIN(?eventAcronym) as ?acronym)
   (COUNT (DISTINCT ?eventAcronym) as ?acronymCount)
   (GROUP_CONCAT(DISTINCT ?eventAcronym; SEPARATOR="| ") AS ?acronyms)

   (MIN(?eventVariant) as ?variant)
   (COUNT (DISTINCT ?eventVariant) as ?variantCount)
   (GROUP_CONCAT(DISTINCT ?eventVariant; SEPARATOR="| ") AS ?variants) 

   (MIN(?eventPlace) as ?place)
   (COUNT (DISTINCT ?eventPlace) as ?placeCount)
   (GROUP_CONCAT(DISTINCT ?eventPlace; SEPARATOR="| ") AS ?places) 

   (MIN(?eventHomepage) as ?homepage)
WHERE {
  ?event a gnd:ConferenceOrEvent.
  ?event gnd:gndIdentifier ?eventId.
  ?event gnd:preferredNameForTheConferenceOrEvent ?eventTitle.
  OPTIONAL { ?event gnd:abbreviatedNameForTheConferenceOrEvent ?eventAcronym. }
  OPTIONAL { ?event gnd:homepage ?eventHomepage. }
  OPTIONAL { ?event gnd:variantNameForTheConferenceOrEvent ?eventVariant. }
  OPTIONAL { ?event gnd:dateOfConferenceOrEvent ?eventDate. }
  OPTIONAL { ?event gnd:placeOfConferenceOrEvent ?eventPlace }
  # only available 3520 times 2021-12
  # ?event gnd:topic ?topic.
  # only available 12106 times 2021-12
  # ?event gnd:precedingConferenceOrEvent ?prec
  # only available 11929 times 2021-12
  #?event gnd:succeedingConferenceOrEvent ?succ
}
GROUP BY ?event ?eventId
LIMIT %d""" % (GND.limit)
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
        