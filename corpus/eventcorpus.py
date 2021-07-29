'''
Created on 2021-04-16

@author: wf
'''

from corpus.event import EventManager, EventSeriesManager

class EventDataSource(object):
    '''
    a data source for events
    '''
    
    def __init__(self,name:str,eventManager:EventManager,eventSeriesManager:EventSeriesManager):
        '''
        constructor
        
        Args:
            name(str): the name of the data source
            eventManager(EventManager): manager for the events
            eventSeriesManager(EventSeriesManager): manager for the eventSeries
        '''
        self.name=name
        self.eventManager=eventManager
        self.eventSeriesManager=eventSeriesManager
        
    def load(self,forceUpdate=False):
        '''
        load this data source
        '''
        self.eventSeriesManager.fromCache(force=forceUpdate)
        self.eventManager.fromCache(force=forceUpdate)
        

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

    def addDataSource(self, name:str, eventManager:EventManager, eventSeriesManager:EventSeriesManager):
        '''
        adds the given set as a eventDataSource to the data sources of this EventCorpus
        
        Args:
            name(str): the name of the data source
            eventManager(EventManager): manager for the events
            eventSeriesManager(EventSeriesManager): manager for the eventSeries
        '''
        eventDataSource=EventDataSource(name,eventManager,eventSeriesManager)
        self.eventDataSources[name]=eventDataSource
        pass
    
    def loadAll(self):
        '''
        load all eventDataSources
        '''
        for eventDataSource in self.eventDataSources.values():
            eventDataSource.load()

   
