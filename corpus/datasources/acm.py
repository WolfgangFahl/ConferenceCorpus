'''
Created on 2021-11-04

@author: wf
'''
from corpus.event import Event,EventSeries,EventManager,EventSeriesManager
from lodstorage.storageconfig import StorageConfig
from corpus.eventcorpus import EventDataSourceConfig,EventDataSource
from corpus.datasources.webscrape import WebScrape

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
            
        Return:
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
        
    def eventSeriesFromSoups(self,seriesSoup,proceedingsSoup):
        '''
        create an eventSeries from two beautiful soup parsed html pages
        '''
        acmSeries=AcmEventSeries()
        
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
        super().__init__(name="ConfrefEvents", sourceConfig=ACM.sourceConfig, clazz=AcmEvent, config=config)
        
class AcmEventSeriesManager(EventSeriesManager):
    '''
    event series handling for event series derived from the ACM digital library
    '''
     
    def __init__(self,config:StorageConfig=None):
        '''
        Constructor
        '''
        super().__init__(name="AcmEventSeries", sourceConfig=ACM.sourceConfig,clazz=AcmEventSeries,config=config)

