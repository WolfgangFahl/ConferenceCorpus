'''
Created on 2021-04-16

@author: wf
'''
from corpus.event import EventManager, EventSeriesManager
from corpus.config import EventDataSourceConfig            
from quality.rating import RatingManager

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
        self.eventSeriesManager=eventSeriesManager
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
        
    def rateAll(self,ratingManager:RatingManager):
        '''
        rate all events and series based on the given rating Manager
        '''
        self.eventManager.rateAll(ratingManager)
        self.eventSeriesManager.rateAll(ratingManager)
        

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

    def addDataSource(self, eventDataSource:EventDataSource):
        '''
        adds the given eventDataSource
        
        Args:
            eventDataSource: EventDataSource
        '''
        self.eventDataSources[eventDataSource.sourceConfig.lookupId]=eventDataSource
        pass
    
    def loadAll(self,forceUpdate:bool=False):
        '''
        load all eventDataSources
        
        Args:
            forceUpdate(bool): True if the data should be fetched from the source instead of the cache
        '''
        for eventDataSource in self.eventDataSources.values():
            eventDataSource.load(forceUpdate=forceUpdate)
