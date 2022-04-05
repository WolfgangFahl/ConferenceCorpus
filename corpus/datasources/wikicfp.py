'''
Created on 2021-07-31

@author: wf
'''

from corpus.event import EventStorage,EventSeriesManager, EventSeries, Event, EventManager
from lodstorage.storageconfig import StorageConfig
import corpus.datasources.wikicfpscrape
from corpus.eventcorpus import EventDataSource, EventDataSourceConfig
from corpus.quality.rating import Rating, RatingType
from datetime import datetime
from corpus.datasources import wikicfpscrape
from ptp.ordinal import Ordinal

class WikiCfp(EventDataSource):
    '''
    scientific event from http://www.wikicfp.com
    '''
    sourceConfig = EventDataSourceConfig(lookupId="wikicfp", name="WikiCFP", url='http://www.wikicfp.com', title='WikiCFP', tableSuffix="wikicfp",locationAttribute="locality")
    
    def __init__(self,debug=False):
        '''
        constructor
        '''
        super().__init__(WikiCfpEventManager(), WikiCfpEventSeriesManager(), WikiCfp.sourceConfig)
        self.debug=debug
        config=EventStorage.getStorageConfig(mode='json')
        jsonEventCache=WikiCfpEventManager(config=config)
        jsonEventSeriesCache=WikiCfpEventSeriesManager(config=config)
        self.wikiCfpScrape=corpus.datasources.wikicfpscrape.WikiCfpScrape(jsonEventCache,jsonEventSeriesCache)
    
class WikiCfpEvent(Event):
    '''
    event derived from WikiCFP
    '''
    
    @classmethod
    def getSamples(cls):
        samples = [
        {
            "Notification_Due": datetime.fromisoformat("2008-05-29"),
            "Submission_Deadline": datetime.fromisoformat("2008-04-15"),
            "acronym": "SIGMAP 2008",
            "city": "Porto",
            "country": "Portugal",
            "deleted": False,
            "endDate": datetime.fromisoformat("2008-07-29"),
            "eventType": "Conference",
            "homepage": "http://www.sigmap.org/SIGMAP2008/CallforPapers.html",
            "locality": "Poato, Portugal",
            "lookupAcronym": "SIGMAP 2008",
            "source": "wikicfp",
            "startDate": datetime.fromisoformat("2008-07-26"),
            "title": "SIGMAP  2008 : International Conference on Signal Processing and Multimedia Applications",
            "url": "http://www.wikicfp.com/cfp/servlet/event.showcfp?eventid=977",
            "wikiCFPId": 977,
            "year": 2008
        }]
        return samples
    
    @staticmethod
    def postProcessLodRecord(rawEvent):
        '''
        postProcess the given rawEvent
        
        Args:
            rawEvent(dict): the record to post process
        '''
        rawEvent["source"]="wikicfp"
        if not "url" in rawEvent:
            crawlType=wikicfpscrape.CrawlType.EVENT
            eventId=rawEvent["eventId"]
            rawEvent["url"]=f"{crawlType.urlPrefix}{eventId}"
        Ordinal.addParsedOrdinal(rawEvent)
        
    
    def rate(self,rating:Rating):
        '''
        rate me
        
        Args:
            rating(Rating): the rating to modify
        '''
        rating.set(0, RatingType.ok, "")
        
class WikiCfpEventSeries(EventSeries):
    '''
    event series derived from WikiCFP
    '''
    
    @classmethod
    def getSamples(cls):
        samples = [
            {
                "dblpSeriesId": "conf/aaai",
                "seriesId": "3",
                "title": "AAAI: National Conference on Artificial Intelligence 2022 2021 2020 ...",
                "wikiCfpId": 3
            }
        ]
        return samples
    
    @staticmethod
    def postProcessLodRecord(rawEvent):
        '''
        postProcess the given rawEvent
        
        Args:
            rawEvent(dict): the record to post process
        '''
        rawEvent["source"]="wikicfp"
        rawEvent["eventSeriesId"]=rawEvent["seriesId"]
        if not "url" in rawEvent:
            crawlType=wikicfpscrape.CrawlType.SERIES
            seriesId=rawEvent["seriesId"]
            rawEvent["url"]=f"{crawlType.urlPrefix}{seriesId}"
        if "title" in rawEvent:
            title=rawEvent["title"]
            if title:
                if ":" in title:
                    rawEvent["acronym"]=title.split(":")[0]
                suffix="2022 2021 2020 ..."
                if title.endswith(suffix):
                    title=title.replace(suffix,"")
            rawEvent["title"]=title
    
    
class WikiCfpEventManager(EventManager):
    '''
    manage WikiCFP derived scientific events
    '''

    def __init__(self, config:StorageConfig=None):
        '''
        Constructor
        '''
        super().__init__(name="WikiCfpEvents", sourceConfig=WikiCfp.sourceConfig,clazz=WikiCfpEvent, config=config)
        
    def configure(self):
        '''
        configure me
        '''
        # no need - getListOfDicts has a specialized implementation
        pass
        
    def getListOfDicts(self):
        '''
        get my list of dicts
        '''
        lod = []
        if  hasattr(self, "dataSource"):
            jsonEm=self.dataSource.wikiCfpScrape.cacheToJsonManager(corpus.datasources.wikicfpscrape.CrawlType.EVENT) 
            for event in jsonEm.events:
                lod.append(event.__dict__)
            self.postProcessLodRecords(lod)
        return lod    

 
class WikiCfpEventSeriesManager(EventSeriesManager):
    '''
    manage WikiCFP derived scientific conference series
    '''

    def __init__(self, config:StorageConfig=None):
        '''
        Constructor
        '''
        super(WikiCfpEventSeriesManager, self).__init__(name="WikiCfpEventSeries", sourceConfig=WikiCfp.sourceConfig, clazz=WikiCfpEventSeries, config=config)
        
    def configure(self):
        '''
        configure me
        '''
        # no need - getListOfDicts has a specialized implementation
        
    def getListOfDicts(self):
        '''
        get my list of dicts
        '''
        lod = []
        if  hasattr(self, "dataSource"):
            jsonEm=self.dataSource.wikiCfpScrape.cacheToJsonManager(corpus.datasources.wikicfpscrape.CrawlType.SERIES)
            for series in jsonEm.series:
                lod.append(series.__dict__)
            self.postProcessLodRecords(lod)
        return lod    
