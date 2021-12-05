'''
Created on 2020-09-15

@author: wf
'''
from corpus.eventcorpus import EventDataSource, EventDataSourceConfig
from corpus.event import EventStorage,EventSeriesManager, EventSeries, Event, EventManager
from lodstorage.storageconfig import StorageConfig

class GND(EventDataSource):
    '''
    manages event data from Gemeinsame Normdatei
    https://d-nb.info/standards/elementset/gnd
    '''
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
        
class GndEvent(Event):
    '''
    a scientific event derived from Gemeinsame Normdatei
    '''
    @classmethod
    def getSamples(cls):
        samples = [      
        ]
        return samples
      
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
        