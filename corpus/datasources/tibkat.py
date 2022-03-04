'''
Created on 2022-02-16

@author: wf
'''
from corpus.eventcorpus import EventDataSource, EventDataSourceConfig
from corpus.event import EventSeriesManager,EventSeries, Event, EventManager
from lodstorage.storageconfig import StorageConfig
from corpus.datasources.tibkatftx import FTXParser
from corpus.datasources.textparse import Textparse
import re

class Tibkat(EventDataSource):
    '''
    TIBKAT event meta data access
    
    https://www.tib.eu
    
    Technische Informationsbibliothek (TIB)
    
    Public datasets available via
    
    https://tib.eu/data/rdf
    
    '''
    sourceConfig = EventDataSourceConfig(lookupId="tibkat", name="tib.eu", url="https://www.tib.eu", title="TIBKAT", tableSuffix="tibkat")
    
    def __init__(self):
        '''
        construct me
        '''
        super().__init__(TibkatEventManager(),TibkatEventSeriesManager(),Tibkat.sourceConfig)

class TibkatEventManager(EventManager):
    '''
    manage TIBKAT derived scientific events
    '''
    def __init__(self,config:StorageConfig=None):
        '''
        Constructor
        '''
        self.source="tibkat"
        super(TibkatEventManager,self).__init__(name="TIBKATEvents", sourceConfig=Tibkat.sourceConfig,clazz=TibkatEvent,config=config)
        
    def configure(self):
        '''
        configure me
        '''
        self.ftxroot="/Volumes/seel/tibkat-ftx/tib-intern-ftx_0/tib-2021-12-20"
        self.wantedbks=["54"] # Informatik
        self.limitFiles=10000
    
    def isWantedBk(self,bk):
        '''
        check whether the given basis klassifikation is in the list of wanted ones
        '''
        for wantedbk in self.wantedbks:
            if bk.startswith(wantedbk):
                return True
        return False
        
    def isInWantedBkDocuments(self,document):
        '''
        filter for wanted Basisklassifikation
        
        Args:
            document(XMLEntity): the document to check
        '''
        wanted=False
        if hasattr(document, "bk"):
            bk=document.bk
            if isinstance(bk,list):
                for bkvalue in bk:
                    wanted=wanted or self.isWantedBk(bkvalue) 
            else:
                wanted=wanted or self.isWantedBk(bk)
        return wanted
         
    def getListOfDicts(self)->list:
        '''
        get my list of dicts
        '''
        lod=[]
        self.ftxParser=FTXParser(self.ftxroot)
        xmlFiles=self.ftxParser.ftxXmlFiles()
        xmlFiles=xmlFiles[:self.limitFiles]
        for xmlFile in xmlFiles:
            xmlPath=f"{self.ftxroot}/{xmlFile}"
            for document in self.ftxParser.parse(xmlPath):
                if self.isInWantedBkDocuments(document):
                    lod.append(document.asDict())
        return lod

class TibkatEvent(Event):
    '''
    event derived from TIBKAT
    '''
    
    def __init__(self):
        '''constructor '''
        super().__init__()
        pass
    
    @classmethod
    def parseDescription(cls,description:str)->dict:
        '''
        parse the given description
        
        Args:
            description(str): an event description
        '''
        result={}
        parts=description.split(";")
        if len(parts)>1:
            title=parts[0]
            titlepattern=r"\((?P<acronym>[^)]*)\)"
            titlematch=re.search(titlepattern,title)
            if titlematch:
                result["acronym"]=titlematch.group("acronym")
            loctime=parts[1]
            #8 (Vietri) : 1996.05.23-25
            loctimepattern=r"\s?(?P<ordinal>[1-9][0-9]*)\s?\((?P<location>[^)]*)\)\s?:\s?(?P<daterange>[12][0-9][0-9][0-9]\.[0-9][0-9]\.[0-9][0-9]\-[0-9][0-9])"
            loctimematch=re.search(loctimepattern,loctime)
            if loctimematch:
                ordinalStr=loctimematch.group("ordinal")
                if ordinalStr is not None:
                    result["ordinal"]=int(ordinalStr)
                locationStr=loctimematch.group("location")
                if locationStr is not None:
                    result['location']=locationStr
                dateRangeStr=loctimematch.group("daterange")
                dateResult=Textparse.getDateRange(dateRangeStr)
                # merge with result
                result={**result, **dateResult}
            pass
            
        return result    
    
class TibkatEventSeriesManager(EventSeriesManager):
    '''
    TIBKAT event series access
     '''

    def __init__(self, config: StorageConfig=None):
        '''
        Constructor
        '''
        super().__init__(name="TibkatEventSeries", sourceConfig=Tibkat.sourceConfig, clazz=TibkatEventSeries, config=config)
        
    def configure(self):
        '''
        configure me
        '''
        
    def getListOfDicts(self)->list:
        '''
        get my list of dicts
        '''
        lod=[{"source":"tibkat"}]
        return lod
        
class TibkatEventSeries(EventSeries):
    '''
    a Tibkat Event Series
    
    '''

    def __init__(self):
        '''constructor '''
        super().__init__()
        pass
