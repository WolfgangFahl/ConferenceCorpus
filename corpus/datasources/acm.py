'''
Created on 2021-11-04

@author: wf
'''
from corpus.event import Event,EventSeries,EventManager,EventSeriesManager
from lodstorage.storageconfig import StorageConfig
from corpus.eventcorpus import EventDataSourceConfig,EventDataSource
from corpus.datasources.webscrape import WebScrape
from corpus.datasources.wikidata import Wikidata

class ACM(EventDataSource):
    '''
    ACM digital library access
    https://dl.acm.org/conferences
    '''
    sourceConfig=EventDataSourceConfig(lookupId="acm",name="acm",url="https://dl.acm.org/conferences",title="Association for Computing machinery",tableSuffix="acm")
  

    def __init__(self,debug:bool=False,showHtml=False):
        '''
        Constructor
        
            debug(bool): True if debugging should be active
            showHtml(bool): True if HTML of scraped websites should be shown
        '''
        super().__init__(AcmEventManager(),AcmEventSeriesManager(),ACM.sourceConfig)
        self.debug=debug
        self.showHtml=showHtml
        
    def getSoup(self,url:str):
        '''
        get the beautiful soup parser result for the given url
        
        Args:
            url(str): the url to parse
            
        Returns:
            BeautifulSoup: the soup
        '''
        msg=f"getting {url} ..."
        if self.debug:
            print (msg)
        scrape=WebScrape(debug=self.debug)
        soup=scrape.getSoup(url, showHtml=self.showHtml)   
        return soup
    
    def eventFromProceedingsDOI(self,doi:str):
        '''
        create an AcmEvent from the given ACM Digital Library Proceedings doi
        
        Args:
            acmDlEventId(doi): ACM Digital Library Proceedings DOI
           
        Return:
            AcmEvent
            
        '''
        url=f"https://dl.acm.org/doi/proceedings/{doi}"
        eventSoup=self.getSoup(url)
        acmEvent=self.eventFromSoup(eventSoup)
        return acmEvent
    
    def eventSeriesfromDigitalLibraryEventId(self,acmDlEventId:str):
        '''
        create an AcmEventSeries from the given ACM Digital Library Event Id
        
        Args:
            acmDlEventId(str): ACM Digital Library Event Id see https://www.wikidata.org/wiki/Property:P3333
        '''
        url=f"https://dl.acm.org/event.cfm?id={acmDlEventId}"
        seriesSoup=self.getSoup(url)
        canonical = seriesSoup.find('link', {'rel': 'canonical'})
        link=canonical['href']
        proceedingsUrl=f"{link}/proceedings"
        proceedingsSoup=self.getSoup(proceedingsUrl)
        acmSeries=self.eventSeriesFromSoups(seriesSoup,proceedingsSoup)
        return acmSeries
        
    def eventSeriesFromSoups(self,seriesSoup,proceedingsSoup,debug=False):
        '''
        create an eventSeries from two beautiful soup parsed html pages
        '''
        acmSeries=AcmEventSeries()
        #debug=True
        if debug:
            seriesHTML = seriesSoup.prettify()
            print (seriesHTML)
        
        return acmSeries
    
    def eventFromSoup(self,eventSoup):
        '''
        create an event from the parsed html page
        '''
        acmEvent=AcmEvent()
        return acmEvent
        
class AcmEvent(Event):
    '''
    a scientific event derived from the ACM digital library
    '''
    
    
class AcmEventSeries(EventSeries):
    '''
    a scientific event series derived from the ACM digital library
    '''
          
class AcmEventManager(EventManager):
    '''
    ACM event manager
    '''
        
    def __init__(self, config: StorageConfig = None):
        '''
        Constructor
        '''
        self.source="acm"
        self.endpoint=Wikidata.endpoint
        super().__init__(name="ACMEvents", sourceConfig=ACM.sourceConfig, clazz=AcmEvent, config=config)

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
        query="""# WF 2021-11-12
# ACM proceedings
SELECT ?doi ?publisher ?publisherLabel ?proc ?procLabel ?event ?eventLabel ?type ?typeLabel ?series ?seriesLabel ?acmConferenceId ?acmEventSeriesId ?gndEventId ?dblpEventSeriesId WHERE {
  # proceedings
  ?proc wdt:P31 wd:Q1143604.
  # publisher ACM
  ?proc wdt:P123 wd:Q127992.
  OPTIONAL {
    ?proc wdt:P123 ?publisher
  }
  # doi
  OPTIONAL {
    ?proc wdt:P356 ?doi.
  }
  OPTIONAL {
    # of an event
    ?proc wdt:P4745 ?event.
    OPTIONAL {
      ?event wdt:P227 ?gndEventId.
    }
    OPTIONAL {
      ?event wdt:P31 ?type.
    } 
    OPTIONAL {
      ?event wdt:P179 ?series
  
      OPTIONAL {
        ?series wdt:P7979 ?acmConferenceId.
      }
      OPTIONAL {
        ?series wdt:P3333 ?acmEventSeriesId.
      }
      OPTIONAL  {
       ?series wdt:P8926 ?dblpEventSeriesId.
      } 
    }
  }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
        """
        return query      
    
class AcmEventSeriesManager(EventSeriesManager):
    '''
    event series handling for event series derived from the ACM digital library
    '''
     
    def __init__(self,config:StorageConfig=None):
        '''
        Constructor
        '''
        self.source="acm"
        self.endpoint=Wikidata.endpoint
        super().__init__(name="AcmEventSeries", sourceConfig=ACM.sourceConfig,clazz=AcmEventSeries,config=config)

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
        query="""# WF 2021-11-04
# ACM event series in Wikidata
SELECT ?eventSeries ?eventSeriesLabel ?acmConferenceId ?acmEventId ?dblpEventId  WHERE {
  # scientific conference series
  ?eventSeries wdt:P31 wd:Q47258130.  
  #?eventSeries wdt:P31 ?type.
  ?eventSeries wdt:P7979 ?acmConferenceId.
  ?eventSeries wdt:P3333 ?acmEventId.
  OPTIONAL  {
    ?eventSeries wdt:P8926 ?dblpEventId.
  }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER by ?acmEventId"""
        return query