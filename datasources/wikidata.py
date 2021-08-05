'''
Created on 2021-07-21

@author: wf
'''
from corpus.event import EventSeriesManager,EventSeries, Event, EventManager
from lodstorage.sparql import SPARQL
from lodstorage.storageconfig import StorageConfig
from corpus.eventcorpus import EventDataSource,EventDataSourceConfig

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
    
class WikidataEvent(Event):
    '''
    event derived from Wikidata
    '''
    
    @staticmethod
    def fixRawEvent(rawEvent:dict):
        '''
        fix the given raw Event
        
        Args:
            rawEvent(dict): the raw event record to fix
        '''
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
        super(WikidataEventManager,self).__init__(name="WikidataEvents", sourceConfig=Wikidata.sourceConfig,clazz=WikidataEvent,config=config)
        
    def configure(self):
        '''
        configure me
        '''
        if not hasattr(self, "getListOfDicts"):
            self.getListOfDicts=self.getLoDfromEndpoint    
   
    def getSparqlQuery(self):
        '''
        get  the SPARQL query for this series
        
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
  #?eventLabel
  ?title
  ?locationLabel 
  #?countryIdLabel
  ?country
  ?countryId
  ?eventInSeries
  ?eventInSeriesId
  ?startDate
  ?endDate
  ?homepage 
  ?dblpConferenceId
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
  # ordinal
  OPTIONAL { ?event wdt:P1545 ?ordinal }
  # properties with type:literal # requiring label
  OPTIONAL { ?event wdt:P276 ?location . }
  OPTIONAL { 
      ?event wdt:P17 ?countryId . 
      ?countryId rdfs:label ?country filter (lang(?country)   = "en").
  }
  OPTIONAL {
      ?event wdt:P276 ?locationId.
      ?locationId rdfs:label ?location filter (lang(?location)   = "en").
  }
  OPTIONAL { 
    ?event wdt:P179 ?eventInSeriesId . 
    ?eventInSeriesId rdfs:label ?eventInSeries filter (lang(?eventInSeries)   = "en").
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
  OPTIONAL { ?event wdt:P8926 ?dblpConferenceId . } 
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
    
    def getLoDfromEndpoint(self,endpoint=Wikidata.endpoint):
        '''
        get my content from the given endpoint
        '''
        sparql=SPARQL(endpoint)
        query=self.getSparqlQuery()
        listOfDicts=sparql.queryAsListOfDicts(query)
        self.setAllAttr(listOfDicts,"source","dblp")
        for rawEvent in listOfDicts:
            WikidataEvent.fixRawEvent(rawEvent)
        return listOfDicts
    
class WikidataEventSeriesManager(EventSeriesManager):
    '''
    wikidata scientific conference Series Manager
    '''

    def __init__(self,config:StorageConfig=None):
        '''
        Constructor
        '''
        super(WikidataEventSeriesManager,self).__init__(name="WikidataEventSeries", sourceConfig=Wikidata.sourceConfig,clazz=WikidataEventSeries,config=config)
        
    def configure(self):
        '''
        configure me
        '''
        if not hasattr(self, "getListOfDicts"):
            self.getListOfDicts=self.getLoDfromEndpoint
        
    def getSparqlQuery(self):
        '''
        get  the SPARQL query for this series
        '''
        query="""
        # Conference Series wikidata query
        # see https://confident.dbis.rwth-aachen.de/dblpconf/wikidata
        # WF 2021-01-30
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT (?confSeries as ?eventSeriesId) ?acronym ?confSeriesLabel ?official_website ?DBLP_pid ?WikiCFP_pid ?FreeBase_pid ?Microsoft_Academic_pid ?Publons_pid ?ACM_pid ?GND_pid
        WHERE 
        {
          #  scientific conference series (Q47258130) 
          ?confSeries wdt:P31 wd:Q47258130.
          OPTIONAL { ?confSeries wdt:P1813 ?short_name . }
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

    def getLoDfromEndpoint(self,endpoint=Wikidata.endpoint)->list:
        '''
        get my content from the given endpoint
        '''
        sparql=SPARQL(endpoint)
        query=self.getSparqlQuery()
        listOfDicts=sparql.queryAsListOfDicts(query)
        self.setAllAttr(listOfDicts,"source","wikidata")
        return listOfDicts
            
        
        