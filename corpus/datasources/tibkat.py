'''
Created on 2022-02-16

@author: wf
'''
from corpus.eventcorpus import EventDataSource, EventDataSourceConfig
from corpus.event import EventSeriesManager,EventSeries, Event, EventManager
from lodstorage.storageconfig import StorageConfig
from corpus.datasources.tibkatftx import FTXParser
from corpus.utils.textparse import Textparse
import re
from corpus.utils.progress import Progress
from pathlib import Path
class Tibkat(EventDataSource):
    '''
    TIBKAT event meta data access
    
    https://www.tib.eu
    
    Technische Informationsbibliothek (TIB)
    
    Public datasets available via
    
    https://tib.eu/data/rdf
    
    '''
    sourceConfig = EventDataSourceConfig(lookupId="tibkat", name="tib.eu", url="https://www.tib.eu", title="TIBKAT", tableSuffix="tibkat",locationAttribute="location")
    home = str(Path.home())
    # use a symbolic link if you want a different location
    ftxroot=f"{home}/.conferencecorpus/tibkat/ftx"
    wantedbks=["54"] # Informatik
    limitFiles=10000
  
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
    
    def isWantedBk(self,bk):
        '''
        check whether the given basisklassifikation bk is in the list of wanted ones
        
        Args:
            bk(str): the basisklassifkation to check
        '''
        for wantedbk in Tibkat.wantedbks:
            if bk.startswith(wantedbk):
                return True
        return False
        
    def isInWantedBkDocuments(self,document):
        '''
        filter for wanted Basisklassifikation
        
        Args:
            document(XMLEntity): the document to check
        '''
        if len(Tibkat.wantedbks)==0:
            return True
        wanted=False
        if hasattr(document, "bk"):
            bk=document.bk
            if isinstance(bk,list):
                for bkvalue in bk:
                    wanted=wanted or self.isWantedBk(bkvalue) 
            else:
                wanted=self.isWantedBk(bk)
        return wanted
         
    def getListOfDicts(self)->list:
        '''
        get my list of dicts
        '''
        lod=[]
        self.ftxParser=FTXParser(Tibkat.ftxroot)
        xmlFiles=self.ftxParser.ftxXmlFiles()
        xmlFiles=xmlFiles[:Tibkat.limitFiles]
        progress=Progress(progressSteps=1,expectedTotal=len(xmlFiles),msg=f"parsing {len(xmlFiles)} TIBKAT FTX files",showMemory=True)
        for xmlFile in xmlFiles:
            for document in self.ftxParser.parse(xmlFile,local=True):
                if self.isInWantedBkDocuments(document):
                    rawEvent=document.asDict()
                    TibkatEvent.postProcessLodRecord(rawEvent)
                    lod.append(rawEvent)
            progress.next()
        progress.done()
        return lod

class TibkatEvent(Event):
    '''
    event derived from TIBKAT
    '''
    
    def __init__(self):
        '''constructor '''
        super().__init__()
        pass
    
    @staticmethod
    def postProcessLodRecord(rawEvent:dict):
        '''
        fix the given raw Event
        
        Args:
            rawEvent(dict): the raw event record to fix
        '''
        rawEvent["source"]="tibkat"
        rawEvent["eventId"]=rawEvent["ppn"]
        if "description" in rawEvent:
            description=rawEvent["description"]
            if isinstance(description,list):
                parseResults=[]
                # find shortes Acronym
                for descEntry in description:
                    parseResult=TibkatEvent.parseDescription(descEntry)
                    if 'acronym' in parseResult and 'ordinal' in parseResult:
                        parseResults.append(parseResult)   
                parseResultsByAcronymLen = sorted(parseResults, key=lambda rawEvent: len(rawEvent['acronym']))             
                if len(parseResultsByAcronymLen)>0:
                    shortestAcronymDescriptionResult=parseResultsByAcronymLen[0]
                    TibkatEvent.mergeDict(rawEvent, shortestAcronymDescriptionResult)
            else:
                TibkatEvent.mergeDescription(description, rawEvent)
        pass
    
    @classmethod
    def mergeDict(cls,rawEvent:dict,more:dict):
        for key in more:
            rawEvent[key]=more[key]
    
    @classmethod
    def mergeDescription(cls,description:str,rawEvent:dict):
        parseResult=TibkatEvent.parseDescription(description)
        TibkatEvent.mergeDict(rawEvent, parseResult)
        
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
            else:
                result["acronym"]=title.strip()
            loctime=parts[1]
            #8 (Vietri) : 1996.05.23-25
            loctimepattern=r"\s?(?P<ordinal>[1-9][0-9]*)\s?\((?P<location>[^)]*)\)\s?:\s?(?P<daterange>[12][0-9][0-9][0-9]\.[0-9][0-9]\.[0-9][0-9]\-([0-9][0-9]\.[0-9][0-9]|[0-9][0-9]))"
            loctimematch=re.search(loctimepattern,loctime)
            if loctimematch:
                ordinalStr=loctimematch.group("ordinal")
                if ordinalStr is not None:
                    ordinal=int(ordinalStr)
                    # check for "year" ordinals
                    if ordinal>1000:
                        # completely ignore description 
                        return {}
                    result["ordinal"]=ordinal
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
