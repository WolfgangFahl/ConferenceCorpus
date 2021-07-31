'''
Created on 2021-04-16

@author: wf
'''
from corpus.event import EventManager, EventSeriesManager
from lodstorage.entity import EntityManager
from lodstorage.sql import SQLDB
from lodstorage.storageconfig import StoreMode

class EventDataSourceConfig(object):
    '''
    holds configuration parameters for an EventDataSource
    '''
    def __init__(self,lookupId:str,name:str,title:str,url:str,tablePrefix:str):
        '''
        constructor 
        
        Args:
          lookupId(str): the id of the data source
          name(str): the name of the data source
          title(str): the title of the data source
          url(str): the link to the data source homepage
          tablePrefix(str): the tablePrefix to use
        '''  
        self.lookupId=lookupId
        self.name=name
        self.title=title
        self.url=url
        self.tablePrefix=tablePrefix

class EventDataSource(object):
    '''
    a data source for events
    '''
    
    def __init__(self,eventManager:EventManager,eventSeriesManager:EventSeriesManager,sourceConfig=EventDataSourceConfig):
        '''
        constructor
        
        Args:
            sourceConfig(EventDataSourceConfig): the configuration for the EventDataSource
            eventManager(EventManager): manager for the events
            eventSeriesManager(EventSeriesManager): manager for the eventSeries
        '''
        self.sourceConfig=sourceConfig
        self.name=self.sourceConfig.name
        self.eventManager=eventManager
        self.eventManager.tableName=f"{self.sourceConfig.tablePrefix}_Event"
        self.eventSeriesManager=eventSeriesManager
        self.eventSeriesManager.tableName=f"{self.sourceConfig.tablePrefix}_EventSeries"
        pass
        
    def load(self,forceUpdate=False):
        '''
        load this data source
        '''
        self.eventSeriesManager.configure()
        self.eventManager.configure()
        self.eventSeriesManager.fromCache(force=forceUpdate)
        self.eventManager.fromCache(force=forceUpdate)
        # TODO use same foreign key in all dataSources
        self.eventManager.linkSeriesAndEvent(self.eventSeriesManager,"inEventSeries")
        

class EventCorpus(object):
    '''
    Towards a gold standard event corpus  and observatory ...
    '''

    def __init__(self,debug=False,verbose=False):
        '''
        Constructor
        
        Args:
            debug(bool): set debugging if True
            verbose(bool): set verbose output if True
        '''
        self.debug=debug
        self.verbose=verbose
        self.eventDataSources={}

    def addDataSource(self, eventManager:EventManager, eventSeriesManager:EventSeriesManager, lookupId:str,name:str, title:str, url:str,tablePrefix:str):
        '''
        adds the given set as a eventDataSource to the data sources of this EventCorpus
        
        Args:
            eventManager(EventManager): manager for the events
            eventSeriesManager(EventSeriesManager): manager for the eventSeries
            lookupId(str): the id of the data source
            name(str): the name of the data source
            title(str): the title of the data source
            url(str): the link to the data source homepage
            tablePrefix(str): the tablePrefix to use
        '''
        eventDataSourceConfig=EventDataSourceConfig(lookupId,name,title,url,tablePrefix)
        eventDataSource=EventDataSource(eventManager,eventSeriesManager,eventDataSourceConfig)
        self.eventDataSources[lookupId]=eventDataSource
        pass
    
    def loadAll(self,forceUpdate:bool=False):
        '''
        load all eventDataSources
        
        Args:
            forceUpdate(bool): True if the data should be fetched from the source instead of the cache
        '''
        for eventDataSource in self.eventDataSources.values():
            eventDataSource.load(forceUpdate=forceUpdate)
