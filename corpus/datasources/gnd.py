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
    endpoint="https://confident.dbis.rwth-aachen.de/jena/gnd/sparql"
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
        sparql="""# get events with most often used columns from GND
# plus acronym, topic, homepage (seldom but useful)
# WF 2020-07-12
PREFIX gndi:  <https://d-nb.info/gnd>
PREFIX gnd:  <https://d-nb.info/standards/elementset/gnd#>
PREFIX gndo: <https://d-nb.info/standards/vocab/gnd/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX dc: <http://purl.org/dc/terms/>
PREFIX wdrs: <http://www.w3.org/2007/05/powder-s#>

SELECT  ?event ?eventId ?acronym  ?sameAs ?variant ?title ?date ?areaCode ?place ?topic ?homepage ?prec ?succ
WHERE {
  ?event a gnd:ConferenceOrEvent.
  ?event gnd:gndIdentifier ?eventId.
  OPTIONAL { ?event gnd:abbreviatedNameForTheConferenceOrEvent ?acronym. }
  OPTIONAL { ?event owl:sameAs ?sameAs. }
  OPTIONAL { ?event gnd:variantNameForTheConferenceOrEvent ?variant.}
  OPTIONAL { ?event gnd:preferredNameForTheConferenceOrEvent ?title.}
  OPTIONAL { ?event gnd:dateOfConferenceOrEvent ?date. }
  OPTIONAL { ?event gnd:geographicAreaCode ?areaCode. }
  OPTIONAL { ?event gnd:placeOfConferenceOrEvent ?place. }
  OPTIONAL { ?event gnd:topic ?topic. }
  OPTIONAL { ?event gnd:homepage ?homepage. }
  OPTIONAL { ?event gnd:precedingConferenceOrEvent ?prec }.
  OPTIONAL { ?event gnd:succeedingConferenceOrEvent ?succ }.
}
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
        