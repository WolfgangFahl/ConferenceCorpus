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
    
    @classmethod
    def getSamples(cls):
        samples=[
        {
            "Notification_Due": "2008-05-29",
            "Submission_Deadline": "2008-04-15",
            "acronym": "SIGMAP 2008",
            "city": "Porto",
            "country": "Portugal",
            "deleted": False,
            "endDate": "2008-07-29",
            "eventType": "Conference",
            "homepage": "http://www.sigmap.org/SIGMAP2008/CallforPapers.html",
            "locality": "Poato, Portugal",
            "lookupAcronym": "SIGMAP 2008",
            "source": "wikicfp",
            "startDate": "2008-07-26",
            "title": "SIGMAP  2008 : International Conference on Signal Processing and Multimedia Applications",
            "url": "http://www.wikicfp.com/cfp/servlet/event.showcfp?eventid=977",
            "wikiCFPId": 977,
            "year": 2008
        }]
        return samples
    
    
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
   
        