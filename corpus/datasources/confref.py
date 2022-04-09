'''
Created on 2020-07-11

@author: wf
'''
import html
import re
import os
import json
from corpus.event import Event,EventSeries,EventManager,EventSeriesManager
from corpus.eventcorpus import EventDataSourceConfig,EventDataSource
from lodstorage.storageconfig import StorageConfig
from lodstorage.sql import SQLDB
from ptp.ordinal import Ordinal

class Confref(EventDataSource):
    '''
    ConfRef platform
    '''
    sourceConfig=EventDataSourceConfig(lookupId="confref",name="confref.org",url="http://portal.confref.org",title="ConfRef",tableSuffix="confref",locationAttribute="location")
    
    def __init__(self):
        '''
        construct me 
        '''
        super().__init__(ConfrefEventManager(),ConfrefEventSeriesManager(),Confref.sourceConfig)

    @staticmethod
    def htmlUnEscapeDict(htmlDict:dict):
        '''
        perform html unescaping on the given dict
        
        Args:
            htmlDict(dict): the dictionary to unescape
        '''
        for key in htmlDict:
            value=htmlDict[key]
            if value is not None and type(value) is str:
                value=html.unescape(value)
                htmlDict[key]=value
                
class ConfrefEvent(Event):
    '''
    a scientific event derived from Confref
    '''
    
    @staticmethod
    def postProcessLodRecord(rawEvent:dict):
        '''
        fix the given raw Event
        
        Args:
            rawEvent(dict): the raw event record to fix
        '''
        Confref.htmlUnEscapeDict(rawEvent)
        
        eventId=rawEvent.pop('id')
        # rename number to ordinal
        if 'number' in rawEvent:
            rawEvent['ordinal']=rawEvent.pop('number')
        # handle area and confSeries dicts
        _area=rawEvent.pop('area')
        if isinstance(_area,dict):
            Confref.htmlUnEscapeDict(_area)
            rawEvent["area"]=_area["value"]
            pass
        _confSeries=rawEvent.pop('confSeries')
        if isinstance(_confSeries,dict):
            # dict: 
            #   {'id': 'btw', 
            #    'issn': None, 
            #    'eissn': None, 
            #    'dblpId': 'https://dblp.org/db/conf/btw/', 
            #    'name': 'Datenbanksysteme für Business, Technologie und Web Datenbanksysteme in Büro, Technik und Wissenschaft', 
            #    'description': None
            #  }
            #
            Confref.htmlUnEscapeDict(_confSeries)
            dblpSeriesId=_confSeries["dblpId"]
            if dblpSeriesId is not None:
                m=re.match("https://dblp.org/db/(.*)/",dblpSeriesId) 
                if m:
                    dblpSeriesId=m.group(1)
            rawEvent['dblpSeriesId']=dblpSeriesId
            rawEvent['seriesId']=_confSeries["id"]
            rawEvent['seriesTitle']=_confSeries["name"]   
            rawEvent['seriesIssn']=_confSeries["issn"]
            rawEvent['seriesEissn']=_confSeries["eissn"]
        rawEvent['eventId']=eventId
        rawEvent['url']=f'http://portal.confref.org/list/{eventId}'        
        rawEvent['title']=rawEvent.pop('name')
        rawEvent["source"]="confref"
        location=None
        if "city" in rawEvent and "country" in rawEvent:
            location=f"""{rawEvent["city"]},{rawEvent["country"]}"""
        rawEvent["location"]=location
        Ordinal.addParsedOrdinal(rawEvent)
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
            lod.append(rawEvent)
        self.postProcessLodRecords(lod)
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
        query="""select dblpSeriesId as eventSeriesId,acronym,seriesTitle as title,count(*) as count,min(year) as minYear,max(year) as maxYear
from event_confref
where dblpSeriesId is not Null
group by dblpSeriesId"""
        sqlDB=SQLDB(self.getCacheFile())
        listOfDicts=sqlDB.query(query)
        self.setAllAttr(listOfDicts, "source", "confref")
        self.postProcessLodRecords(listOfDicts)
        return listOfDicts
 