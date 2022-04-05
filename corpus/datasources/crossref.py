'''
Created on 2020-07-05

@author: wf
'''
import habanero
from ptp.ordinal import Ordinal
from corpus.event import Event, EventSeries, EventManager, EventSeriesManager
from lodstorage.storageconfig import StorageConfig
from lodstorage.lod import LOD
import json
import re
import glob
import os
import time
from datetime import datetime

from corpus.eventcorpus import EventDataSource, EventDataSourceConfig


class Crossref(EventDataSource):
    '''
        Access to Crossref's search api see https://github.com/CrossRef/rest-api-doc
    '''
    sourceConfig = EventDataSourceConfig(lookupId="crossref", name="crossref.org", url="https://www.crossref.org/", title="CrossRef", tableSuffix="crossref",locationAttribute="location")
    cr = habanero.Crossref()  
       
    def __init__(self):
        '''
        constructor
        '''
        super().__init__(CrossrefEventManager(), CrossrefEventSeriesManager(), Crossref.sourceConfig)
     
    @classmethod 
    def doiMetaData(cls, doi):
        ''' get the meta data for the given doi '''
        metadata = None
        response = cls.cr.works([doi])
        if 'status' in response and 'message' in response and response['status'] == 'ok':
            metadata = response['message']
        return metadata
    
    @staticmethod    
    def fixEncodings(eventInfo:dict, debug:bool=False): 
        '''
        fix the encoding of the dict entries of the given eventInfo
        
        Args:
            eventInfo(dict): the record to fix
            debug(bool): show debug information if True
        '''
        for keyValue in eventInfo.items():
            key, value = keyValue
            oldvalue = value
            if isinstance(value, str):
                # work around Umlaut encodings like "M\\"unster"
                # and \S encoded as \\S
                found = False
                # see also https://github.com/WolfgangFahl/ProceedingsTitleParser/issues/38
                # remove encoded CR 
                for umlautTuple in [('\\"a', "ä"), ('\\"o', "ö"), ('\\"u', "ü"), ('\\', ' '), ('&#x0D;', '')]:
                    uc, u = umlautTuple
                    if uc in value:
                        value = value.replace(uc, u)
                        found = True  
                if found:
                    if debug:
                        print("Warning: fixing '%s' to '%s'" % (oldvalue, value))
                    eventInfo[key] = value   

    
class CrossrefEvent(Event):
    '''
    a scientific event derived from Crossref
    '''

    @classmethod
    def getSamples(cls):
        samples = [
            {
                "acronym": "SIGMIS CPR '06",
                "doi": "10.1145/1125170",
                "endDate": datetime.fromisoformat("2006-04-15"),
                "eventId": "10.1145/1125170",
                "location": "Claremont, California, USA",
                "month": 4,
                "name": "the 2006 ACM SIGMIS CPR conference",
                "number": "44",
                "source": "crossref",
                "sponsor": "SIGMIS, ACM Special Interest Group on Management Information Systems,ACM, Association for Computing Machinery",
                "startDate": datetime.fromisoformat("2006-04-13"),
                "theme": "Forty four years of computer personnel research: achievements, challenges & the future",
                "title": "Proceedings of the 2006 ACM SIGMIS CPR conference on computer personnel research Forty four years of computer personnel research: achievements, challenges & the future - SIGMIS CPR '06",
                "url": "https://api.crossref.org/v1/works/10.1145/1125170",
                "year": 2006
            }    
        ]
        return samples
    
    @classmethod
    def fromDOI(cls,doi:str):
        '''
        create a CrossRef Event from the given DOI
        
        Args:
           doi(str): the doi to get a CrossRef event for
        '''
        metadata=Crossref.doiMetaData(doi)
        event=CrossrefEvent()
        event.source='crossref'
        event.mapFromDict(metadata, [('doi','doi'),('ISBN','isbn'),('URL','url')])        
        if 'event' in metadata:
            eventdata=metadata['event']
            event.mapFromDict(eventdata,[('acronym','acronym'),('name','title')])          
        event.metadata=metadata
        return event
        

    
class CrossrefEventSeries(Event):
    '''
    a scientific event series derived from Crossref
    '''
      

class CrossrefEventManager(EventManager):
    '''
    Crossref event manager
    '''
        
    def __init__(self, config: StorageConfig=None):
        '''
        Constructor
        '''
        super().__init__(name="CrossrefEvents", sourceConfig=Crossref.sourceConfig, clazz=CrossrefEvent, config=config)
        
    def configure(self):
        '''
        configure me
        '''
        # nothing to do - there is a get ListOfDicts below    
        
    def getListOfDicts(self):
        '''
        cache my json files to my eventmanager
        '''
        startTime = time.time()
        jsonFiles = self.jsonFiles()
        lod = []
        if len(jsonFiles) < 50:
            print ("not enough crossref json files - did getsamples fail due to crossref API issues?")
            print ("need to download cached version of json files as a work-around instead")  #
            raise Exception(f"only {len(jsonFiles)} crossref json files available - there should be at least 47")
            # url="http://wiki.bitplan.com/images/confident/Event_crossref.db"
            # filename=self.em.getCacheFile(mode=StoreMode.SQL)
            # urllib.request.urlretrieve(url, filename)
        for jsonFilePath in jsonFiles:
            eventBatch = self.fromJsonFile(jsonFilePath)
            if self.debug:
                print("%4d: %s" % (len(eventBatch), jsonFilePath))
            for eventInfo in eventBatch:
                rawEvent = self.postProcess(eventInfo)
                lod.append(rawEvent)
                    
        if self.profile:
            elapsed = time.time() - startTime
            print (f"read {len(lod)} events in {elapsed:5.1f} s")
        return lod
        
    def postProcess(self, eventInfo:dict) -> dict:
        '''
        postProcess the given eventInfo e.g.
         {
        "event": {
          "name": "Adriatico Research Conference and Workshop",
          "location": "ICTP, Trieste, Italy"
        },
        "title": [
          "Towards the Theoretical Understanding of High Tc Superconductors"
        ],
        "DOI": "10.1142/0638"
      },

        '''
        rawEvent = eventInfo['event']
        rawEvent['source'] = "crossref"
        if 'title' in eventInfo:
            title = eventInfo["title"][0]
            rawEvent['title'] = title
            Ordinal.addParsedOrdinal(rawEvent)
        if 'sponsor' in eventInfo:
            sponsor = eventInfo['sponsor'][0]
            rawEvent['sponsor'] = sponsor    
        Crossref.fixEncodings(rawEvent, self.debug)
                            
        doi = eventInfo["DOI"]
        rawEvent['eventId'] = doi
        rawEvent['doi'] = doi
        if 'start' in rawEvent: 
            self.fixDateParts(rawEvent, 'start')
        if 'end'   in rawEvent: 
            self.fixDateParts(rawEvent, 'end')
        LOD.setNone(rawEvent, ['lookupAcronym', 'location', 'number', 'sponsor', 'month', 'year', 'startDate', 'endDate'])
        if 'year' in eventInfo:
            year = eventInfo["year"]
            if year is not None and type(year) is tuple:
                year = year[0]
                if not year in rawEvent:
                    rawEvent["year"] = int(year)
        rawEvent["url"] = f"https://api.crossref.org/v1/works/{doi}" 
        return rawEvent
        
    def fixDateParts(self, rawEvent:dict, key:str):
        '''
        fix date-parts from the json dict created by crossref e.g.
        "date-parts": [
              [
                1999,
                9,
                5
              ]
            ]
            
        Args:
            rawEvent(dict): the dictionary as parsed by json
            key(str): "start" or "end"

        '''
        if 'date-parts' in rawEvent[key]:
            # get the date-parts to be converted
            dateparts = rawEvent[key]['date-parts']
            # remove the original dict
            rawEvent.pop(key) 
            # get the tuple of values
            datetuple = tuple(dateparts[0])
            # set the year and month default
            year = None
            month = None
            # depending on the date tuples length we get more or less information
            if len(datetuple) == 3:
                # a fully specified date
                year, month, day = datetuple
                dt = datetime(year=year, month=month, day=day)
                date = dt.date()
                rawEvent[f"{key}Date"] = date
            elif len(datetuple) == 2:
                # year and month only
                year, month = datetuple
            elif len(datetuple) == 1:
                # year only
                year = datetuple[0] 
            else:
                if self.debug:
                    print(f"warning invalid date-tuple {str(datetuple)} found")
            if key == "start": 
                if year is not None: rawEvent["year"] = year
                if month is not None: rawEvent["month"] = month
    
    def jsonFiles(self) -> list: 
        '''
        get the list of the json files that have my data
        
        Return:
            list: a list of json file names
        
        '''
        cachePath = self.config.getCachePath()
        self.jsondir = f"{cachePath}/crossref"
        if not os.path.exists(self.jsondir):
                os.makedirs(self.jsondir)
        jsonFiles = sorted(glob.glob(f"{self.jsondir}/crossref-*.json"), key=lambda path:int(re.findall(r'\d+', path)[0]))
        return jsonFiles
    
    def fromJsonFile(self, jsonFilePath):
        '''
        get a single batch of events from the given jsonFilePath
        '''
        eventBatch = None
        with open(jsonFilePath) as jsonFile:
            response = json.load(jsonFile)  
            if 'status' in response:
                if response['status'] == 'ok':
                    eventBatch = response['message']['items']
        return eventBatch

    
class CrossrefEventSeriesManager(EventSeriesManager):
    '''
    CrossRef event series handling
    '''
    
    def __init__(self, config:StorageConfig=None):
        '''
        Constructor
        '''
        super().__init__(name="CrossrefEventSeries", sourceConfig=Crossref.sourceConfig, clazz=CrossrefEventSeries, config=config)

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
        lod = [{'source':'crossref', 'eventSeriesId':'dummy'}]
        return lod
