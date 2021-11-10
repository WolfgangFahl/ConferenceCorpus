'''
Created on 2021-07-21

@author: wf
'''
from corpus.event import EventSeriesManager,EventSeries, Event, EventManager
from lodstorage.storageconfig import StorageConfig
from corpus.eventcorpus import EventDataSource,EventDataSourceConfig
import re

class Wikidata(EventDataSource):
    '''
    Wikidata access via SPARQL endpoint
    
    make do not want to be dependend on this endpoint since we might have
    our own copy of Wikidata which might run on Virtuoso or Jena instead of blazegraph
    '''
    endpoint="https://query.wikidata.org/sparql"
    sourceConfig=EventDataSourceConfig(lookupId="wikidata",name="Wikidata",url='https://www.wikidata.org/wiki/Wikidata:Main_Page',title='Wikidata',tableSuffix="wikidata")
    
    def __init__(self):
        '''
        construct me
        '''
        super().__init__(WikidataEventManager(),WikidataEventSeriesManager(),Wikidata.sourceConfig)
        
class WikidataEventSeries(EventSeries):
    '''
    event series derived from Wikidata
    '''
    
    @staticmethod
    def postProcessLodRecord(rawEvent:dict):
        '''
        fix the given raw EventSeries
        
        Args:
            rawEvent(dict): the raw event record to fix
        '''
        rawEvent["source"]="wikidata"
        for key in ["eventSeriesId"]:
            if key in rawEvent:
                rawEvent["url"]=rawEvent[key]
                rawEvent[key]=rawEvent[key].replace("http://www.wikidata.org/entity/","")
    
class WikidataEvent(Event):
    '''
    event derived from Wikidata
    '''
    
    @staticmethod
    def postProcessLodRecord(rawEvent:dict):
        '''
        fix the given raw Event
        
        Args:
            rawEvent(dict): the raw event record to fix
        '''
        rawEvent["source"]="wikidata"
        for key in ["eventId","countryId","locationId","eventInSeriesId"]:
            if key in rawEvent:
                rawEvent[key]=rawEvent[key].replace("http://www.wikidata.org/entity/","")
        if 'startDate' in rawEvent:
            startDate=rawEvent['startDate']
            if startDate:
                rawEvent['year']=startDate.year
                pass
    
class WikidataEventManager(EventManager):
    '''
    manage wikidata derived scientific events
    '''
    def __init__(self,config:StorageConfig=None):
        '''
        Constructor
        '''
        self.source="wikidata"
        self.endpoint=Wikidata.endpoint
        super(WikidataEventManager,self).__init__(name="WikidataEvents", sourceConfig=Wikidata.sourceConfig,clazz=WikidataEvent,config=config)
        
    def configure(self):
        '''
        configure me
        '''
        if not hasattr(self, "getListOfDicts"):
            self.getListOfDicts=self.getLoDfromEndpoint    
   
    def getSparqlQuery(self):
        '''
        get  the SPARQL query for this event manager
        
        see also 
           https://github.com/TIBHannover/confiDent-dataimports/blob/master/wip/wikidata_academic_conferences.rq
           https://confident.dbis.rwth-aachen.de/or/index.php?title=Iteration1_Property_Mapping
        '''
        query="""PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT 
  (?event as ?eventId)
  (?event as ?url)
  ?acronym
  ?ordinal
  ?title
  ?location
  ?locationId 
  ?city
  ?cityId
  ?country
  ?countryId
  ?eventInSeries
  ?eventInSeriesId
  ?followedById
  ?startDate
  ?endDate
  ?homepage 
  ?describedAtUrl
  ?wikiCfpId
  ?gndId
  ?mainSubject
  ?language
 
WHERE
{  
 
  # wdt:P31 (instance of)  wd:Q52260246 (scientific event)
  # Q2020153 (academic conference)
  ?event wdt:P31 wd:Q2020153 .
  # acronym
  OPTIONAL { ?event wdt:P1813 ?acronym }
 
  # properties with type:literal # requiring label
  OPTIONAL { 
      ?event wdt:P17 ?countryId . 
      ?countryId rdfs:label ?country filter (lang(?country)   = "en").
  }
  OPTIONAL {
      ?event wdt:P276 ?locationId.
      ?locationId rdfs:label ?location filter (lang(?location)   = "en").
  }
  OPTIONAL {
      ?event wdt:P276* ?cityId.
      # instance of city
      ?cityId wdt:P31 wd:Q515.
      ?cityId rdfs:label ?city filter (lang(?city)   = "en").
  }
  OPTIONAL { 
    ?event wdt:P179 ?eventInSeriesId . 
    ?eventInSeriesId rdfs:label ?eventInSeries filter (lang(?eventInSeries)   = "en").
    ?event p:P179 ?inSeries.
    OPTIONAL { ?inSeries   pq:P1545 ?ordinal}.
    OPTIONAL { ?inSeries   pq:P156 ?followedById}.
  }
  OPTIONAL { 
    ?event wdt:P2936 ?languageId .
    ?languageId rdfs:label ?language filter (lang(?language)   = "en").
  }
  OPTIONAL { 
    ?event wdt:P921 ?mainSubjectId .
    ?mainSubjectId rdfs:label ?mainSubject filter (lang(?mainSubject)   = "en").
  }
  OPTIONAL { ?event wdt:P580 ?startDate . }
  OPTIONAL { ?event wdt:P582 ?endDate . }
  
  OPTIONAL { ?event wdt:P856 ?homepage . }
  OPTIONAL { ?event wdt:P973 ?describedAtUrl . } 
  OPTIONAL { ?event wdt:P5124 ?wikiCfpId . }
  OPTIONAL { ?event wdt:P227 ?gndId. }
  OPTIONAL { ?event wdt:P214 ?viafId. }
  # labels 
  # works only with WikiData Query Service / blazegraph
  # SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } # provide Label in EN        
  ?event rdfs:label ?title filter (lang(?title)   = "en").
  
}
"""
        return query
    
class WikidataEventSeriesManager(EventSeriesManager):
    '''
    wikidata scientific conference Series Manager
    '''

    def __init__(self,config:StorageConfig=None):
        '''
        Constructor
        '''
        self.source="wikidata"
        self.endpoint=Wikidata.endpoint
        super(WikidataEventSeriesManager,self).__init__(name="WikidataEventSeries", sourceConfig=Wikidata.sourceConfig,clazz=WikidataEventSeries,config=config)
        
    def configure(self):
        '''
        configure me
        '''
        if not hasattr(self, "getListOfDicts"):
            self.getListOfDicts=self.getLoDfromEndpoint
        
    def getSparqlQuery(self):
        '''
        get  the SPARQL query for this series  manager
        '''
        query="""
        # Conference Series wikidata query
        # see https://confident.dbis.rwth-aachen.de/dblpconf/wikidata
        # WF 2021-01-30
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT (?confSeries as ?eventSeriesId) ?acronym ?title ?homepage ?DBLP_pid ?WikiCFP_pid ?FreeBase_pid ?Microsoft_Academic_pid ?Publons_pid ?ACM_pid ?GND_pid
        WHERE 
        {
          #  scientific conference series (Q47258130) 
          ?confSeries wdt:P31 wd:Q47258130.
          OPTIONAL { ?confSeries wdt:P1813 ?short_name . }
          BIND (?confSeriesLabel AS ?title)
          BIND (COALESCE(?short_name,?confSeriesLabel) AS ?acronym).
          #  official website (P856) 
          OPTIONAL {
            ?confSeries wdt:P856 ?homepage
          } 
          # any item with a DBLP venue ID 
          OPTIONAL {
            ?confSeries wdt:P8926 ?DBLP_pid.
          }
          # WikiCFP pid 
          optional {
             ?confSeries wdt:P5127 ?WikiCFP_pid.
          }
          # FreeBase pid
          optional {
              ?confSeries wdt:P646 ?FreeBase_pid.
          }
          # Microsoft Academic ID
          optional {
              ?confSeries wdt:P6366 ?Microsoft_Academic_pid.
          }
          # Publons journals/conferences ID 
          optional {
              ?confSeries wdt:P7461 ?Publons_pid.
          }
          # ACM conference ID   
          optional {
            ?confSeries wdt:P7979 ?ACM_pid.
          }
          # GND pid
          optional {
            ?confSeries wdt:P227 ?GND_pid.
          }
          # label 
          ?confSeries rdfs:label ?confSeriesLabel filter (lang(?confSeriesLabel) = "en").
        }
        ORDER BY (?acronym)
"""
        return query
        
        