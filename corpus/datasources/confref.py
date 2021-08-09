'''
Created on 2020-07-11

@author: wf
'''
from corpus.event import Event,EventSeries,EventManager,EventSeriesManager
from lodstorage.storageconfig import StorageConfig
import html
import os
import json
from corpus.eventcorpus import EventDataSourceConfig,EventDataSource

class Confref(EventDataSource):
    sourceConfig=EventDataSourceConfig(lookupId="confref",name="confref.org",url="http://portal.confref.org",title="ConfRef",tableSuffix="confref")
    
    '''
    ConfRef platform
    '''
    def __init__(self):
        '''
        construct me 
        '''
        super().__init__(ConfrefEventManager(),ConfrefEventSeriesManager(),Confref.sourceConfig)

class ConfrefEvent(Event):
    '''
    a scientific event derived from Confref
    '''
    
    @staticmethod
    def fixRawEvent(rawEvent:dict):
        '''
        fix the given raw Event
        
        Args:
            rawEvent(dict): the raw event record to fix
        '''
        for key in rawEvent:
            value=rawEvent[key]
            if value is not None and type(value) is str:
                value=html.unescape(value)
                rawEvent[key]=value
        eventId=rawEvent.pop('id')
        area=rawEvent.pop('area')
        confSeries=rawEvent.pop('confSeries')
        rawEvent['eventId']=eventId
        rawEvent['url']=f'http://portal.confref.org/list/{eventId}'        
        rawEvent['title']=rawEvent.pop('name')
        rawEvent["source"]="confref"
        pass
    
    def fromDict(self,rawEvent:dict):
        '''
        get me from the given dict
        '''
        super().fromDict(rawEvent)
    
class ConfrefEventSeries(Event):
    '''
    a scientific event series derived from Confref
    '''
        
class ConfrefEventManager(EventManager):
    '''
    Crossref event manager
    '''
        
    def __init__(self, config: StorageConfig = None):
        '''
        Constructor
        '''
        super().__init__(name="ConfrefEvents", sourceConfig=Confref.sourceConfig, clazz=ConfrefEvent, config=config)
        
    def configure(self):
        '''
        configure me
        '''
        # nothing to do - there is a get ListOfDicts below
    
    def getListOfDicts(self):
        '''
        get my content from the json file
        '''
        cachePath=self.config.getCachePath()
        jsondir=f"{cachePath}/confref"
        if not os.path.exists(jsondir):
                os.makedirs(jsondir)
        self.jsonFilePath=f"{jsondir}/confref-conferences.json"
        with open(self.jsonFilePath) as jsonFile:
            rawEvents=json.load(jsonFile)
        lod=[]
        for rawEvent in rawEvents:
            ConfrefEvent.fixRawEvent(rawEvent)
            lod.append(rawEvent)
        return lod
        
class ConfrefEventSeriesManager(EventSeriesManager):
    '''
    Confref event series handling
    '''
    
    def __init__(self,config:StorageConfig=None):
        '''
        Constructor
        '''
        super().__init__(name="ConfrefEventSeries", sourceConfig=Confref.sourceConfig,clazz=ConfrefEventSeries,config=config)


    def configure(self):
        '''
        configure me
        '''
        # nothing to do getListOfDicts is defined
        
    def getListOfDicts(self):
        '''
        get my data
        '''
        # TODO Replace this stub
        lod=[{'source':'crossref','eventSeriesId':'dummy'}]
        return lod