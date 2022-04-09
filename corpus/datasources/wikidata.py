'''
Created on 2021-07-21

@author: wf
'''
from corpus.event import EventSeriesManager,EventSeries, Event, EventManager, EventStorage
from lodstorage.storageconfig import StorageConfig
from corpus.eventcorpus import EventDataSource,EventDataSourceConfig

class Wikidata(EventDataSource):
    '''
    Wikidata access via SPARQL endpoint
    
    make do not want to be dependend on this endpoint since we might have
    our own copy of Wikidata which might run on Virtuoso or Jena instead of blazegraph
    '''
    endpoint="https://query.wikidata.org/sparql"
    sourceConfig=EventDataSourceConfig(lookupId="wikidata",name="Wikidata",url='https://www.wikidata.org/wiki/Wikidata:Main_Page',title='Wikidata',tableSuffix="wikidata",locationAttribute="location")
    
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
        if 'ordinal' in rawEvent:
            try:
                rawEvent['ordinal']=int(rawEvent["ordinal"])
            except Exception as _ex:
                # ignore the invalid ordinal
                del(rawEvent['ordinal'])
                
    
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
        self.queryManager=EventStorage.getQueryManager(lang="sparql",name="wikidata")
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
        eventQuery=self.queryManager.queriesByName['Wikidata-Events']
        query=eventQuery.query
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
        self.queryManager=EventStorage.getQueryManager(lang="sparql",name="wikidata")
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
        eventQuery=self.queryManager.queriesByName['Wikidata-Eventseries']
        query=eventQuery.query
        return query
        
        