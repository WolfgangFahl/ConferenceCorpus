'''
Created on 2021-07-31

@author: wf
'''

from corpus.event import EventSeriesManager,EventSeries, Event, EventManager
from lodstorage.storageconfig import StorageConfig


class WikiCfpEventSeries(EventSeries):
    '''
    event series derived from WikiCFP
    '''
    
class WikiCfpEvent(Event):
    '''
    event derived from WikiCFP
    '''
    
class WikiCfpEventManager(EventManager):
    '''
    manage WikiCFP derived scientific events
    '''
    def __init__(self,config:StorageConfig=None):
        '''
        Constructor
        '''
        super().__init__(name="WikiCfpEvents", clazz=WikiCfpEvent, tableName="wikicfp_event",config=config)
 
class WikiCfpEventSeriesManager(EventSeriesManager):
    '''
    mange WikiCFP derived scientific conference series
    '''

    def __init__(self,config:StorageConfig=None):
        '''
        Constructor
        '''
        super(WikiCfpEventSeriesManager,self).__init__(name="WikiCfpEventSeries", clazz=WikiCfpEventSeries, tableName="wikicfp_eventseries",config=config)
   
        