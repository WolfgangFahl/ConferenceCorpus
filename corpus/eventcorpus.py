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
    def __init__(self,lookupId:str,name:str,title:str,url:str):
        self.lookupId=lookupId
        self.name=name
        self.title=title
        self.url=url

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
        self.eventManager=eventManager
        self.eventSeriesManager=eventSeriesManager
        
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
        
    @staticmethod
    def addEntityManagerTablesToTableMap(tableMap:dict,eventDataSource,entityManager:EntityManager):
        '''
        add the SQL table(s) for the given entity manager to the tableMap
        
        Args:
            tableMap(dict): the map of tables
            eventDataSource(EventDataSource): the event data source
            entityManager(EntityManager): the entityManager to add the tables for
            
        '''
        storeMode=entityManager.config.mode
        if storeMode is StoreMode.SQL:
            sqlDB=SQLDB(entityManager.getCacheFile())
            tableList=sqlDB.getTableList()
            for table in tableList:
                key=f"{eventDataSource.sourceConfig.lookupId}-{entityManager.name}"
                tableMap[key]=table
                pass
        
    def addToTableMap(self,tableMap:dict):
        '''
        get the list of SQL Tables involved and add it to the given tableMap
        
        Return:
            list: the list of SQL tables used for caching
        '''
        EventDataSource.addEntityManagerTablesToTableMap(tableMap,self,self.eventManager)
        EventDataSource.addEntityManagerTablesToTableMap(tableMap,self,self.eventSeriesManager)   

class EventCorpus(object):
    '''
    Towards a gold standard event corpus  and observatory ...
    '''

    def __init__(self,debug=False,verbose=False):
        '''
        Constructor
        '''
        self.debug=debug
        self.verbose=verbose
        self.eventDataSources={}

    def addDataSource(self, eventManager:EventManager, eventSeriesManager:EventSeriesManager, lookupId:str,name:str, title:str, url:str):
        '''
        adds the given set as a eventDataSource to the data sources of this EventCorpus
        
        Args:
            eventManager(EventManager): manager for the events
            eventSeriesManager(EventSeriesManager): manager for the eventSeries
            lookupId(str): the id of the data source
            name(str): the name of the data source
            title(str): the title of the data source
            url(str): the link to the data source homepage
        '''
        eventDataSourceConfig=EventDataSourceConfig(lookupId,name,title,url)
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

    def getTableMap(self)->dict:
        '''
        get the map of SQL Tables involved
        
        Return:
            dict: the map of SQL tables used for caching
        '''
        tableMap={}
        for eventDataSource in self.eventDataSources.values():
            eventDataSource.addToTableMap(tableMap)
        return tableMap
