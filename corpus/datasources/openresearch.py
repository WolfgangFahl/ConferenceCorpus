import urllib
import dateutil.parser
from datetime import datetime
from pathlib import Path
from typing import List, Union, Type
from lodstorage.lod import LOD
from lodstorage.storageconfig import StorageConfig
from wikibot3rd.wikipush import WikiPush
from wikibot3rd.wikiuser import WikiUser
from wikifile.wikiFile import WikiFile
from wikifile.wikiFileManager import WikiFileManager
from wikifile.wikiPage import WikiPage

from corpus.event import Event, EventSeries, EventSeriesManager, EventManager
from corpus.eventcorpus import EventDataSource,EventDataSourceConfig
from corpus.utils.download import Profiler
from ptp.ordinal import Ordinal


class OR(EventDataSource):
    '''
    scientific events from http://www.openresearch.org
    '''

    limitFiles = None
    
    def __init__(self,wikiId='or',via='api'):
        '''
        constructor
        
        Args:
            wikiId(str): the wikiId to get the SMW data from 
            via(str): the access style api or backup
        '''
        lookupId=f"{wikiId}" if via=="api" else f"{wikiId}-backup"
        tableSuffix=f"{wikiId}" if via=="api" else f"{wikiId}backup"
        name=f"{wikiId}-{via}"
        title=f"OPENRESEARCH ({wikiId}-{via})"   
        wikiUser=None 
        try:
            wikiUser=WikiUser.ofWikiId(wikiId, lenient=True)
        except FileNotFoundError as _fne:
            # configuration file missing
            pass
        if wikiUser is not None:
            url=wikiUser.getWikiUrl()
        else:
            if wikiId == "or":
                url = 'https://www.openresearch.org/wiki/Main_Page'
            else:
                url = "https://confident.dbis.rwth-aachen.de/or/index.php?title=Main_Page"
        sourceConfig = EventDataSourceConfig(lookupId=lookupId,
                                             name=name,
                                             url=url,
                                             title=title,
                                             tableSuffix=tableSuffix,
                                             locationAttribute='location')
        eventManager = OREventManager(sourceConfig=sourceConfig, wikiId=wikiId, via=via)
        seriesManager = OREventSeriesManager(sourceConfig=sourceConfig, wikiId=wikiId, via=via)
        super().__init__(eventManager, seriesManager, sourceConfig)


class OREventManager(EventManager):
    '''
    Manager for OpenResearch Events
    
    see https://www.openresearch.org
    '''

    def __init__(self,
                 sourceConfig:EventDataSourceConfig=None,
                 config:StorageConfig=None,
                 wikiId:str='orclone',
                 via:str='api',
                 verbose:bool=False,
                 debug:bool=False):
        '''
        Constructor

        Args:
            sourceConfig(EventDataSourceConfig): event source configuration
            config(StorageConfig): storage configuration
            wikiId(str): wikiId of the event source wiki
            via(str): method the data is retrieved from the api
            verbose(bool):
            debug(bool): If True show debug messages
        '''
        self.events=[]
        super().__init__(name="OREvents",
                         sourceConfig=sourceConfig,
                         clazz=OREvent,
                         primaryKey="pageTitle",
                         config=config)
        self.wikiId = wikiId
        self.via = via
        self.debug=debug
        self.verbose=verbose
        if self.debug:
            self.profile = True
    
    def configure(self):
        '''
        configure me
        '''
        if not hasattr(self, "getListOfDicts"):
            if self.via == 'wikiMarkup':
                self.getListOfDicts = self.getLodFromWikiMarkup
            elif self.via == 'backup':
                self.getListOfDicts = self.getLoDfromWikiFileManager
            else:
                self.getListOfDicts = self.getLoDfromWikiUser

    def getLodFromWikiMarkup(self, limit:int=None) -> List[dict]:
        """
        Retrieves the event records from the WikiMarkup of the event pages.

        Args:
            limit(int): limit number of retrieved records. If None (default) retrieve all event records

        Returns:
            LoD List of event records
        """
        lod = OrSMW.getLodFromWikiMarkup(self.wikiId, OREvent, limit=limit)
        self.setAllAttr(lod, "source", f"{self.wikiId}-wikiMarkup")
        self.postProcessLodRecords(lod, wikiId=self.wikiId, debug=self.debug)
        return lod

    def getLoDfromWikiUser(self, askExtra:str="", profile:bool=False, limit:int=None):
        '''

        Args:
            wikiuser(WikiUser):
            askExtra(str):
            profile(bool):
        '''
        lod = OrSMW.getLodFromWikiApi(self.wikiId, OREvent, askExtra=askExtra, limit=limit, profile=profile)
        self.setAllAttr(lod,"source",f"{self.wikiId}")
        self.postProcessLodRecords(lod,wikiId=self.wikiId, debug=self.debug)
        return lod

    def getLoDfromWikiFileManager(self, wikiFileManager:WikiFileManager=None, limit:int=None):
        '''
        get my list of dicts from the given WikiFileManager

        Args:
            wikiFileManager(WikiFileManager): WikiFileManager from which the records should be loaded
            limit(int): limit the amount on loaded records
        '''
        lod = OrSMW.getLodFromWikiFiles(self.wikiId, OREvent, wikiFileManager=wikiFileManager, limit=limit)
        self.setAllAttr(lod,"source",f"{self.wikiId}-backup")
        self.postProcessLodRecords(lod,wikiId=self.wikiId, debug=self.debug)
        return lod

    @classmethod
    def getPropertyLookup(cls) -> dict:
        '''
        get my PropertyLookupList as a map

        Returns:
            dict: my mapping from wiki property names to LoD attribute Names or None if no mapping is defined
        '''
        lookup = None
        if hasattr(OREvent, 'propertyLookupList'):
            propertyLookupList = OREvent.propertyLookupList
            lookup, _duplicates = LOD.getLookup(propertyLookupList, 'prop')
        return lookup

    def fromWikiUser(self, askExtra: str = "", limit:int=None, profile: bool = False) -> List[dict]:
        '''
        read me from a wiki using the given WikiUser configuration

        Args:
            askExtra(string): Extra query selectors that should be included in the query
            limit(int): limit the amount on loaded records
            profile(bool): If true profile the query. Otherwise, the query runs without tracking the time
        '''
        lod = self.getLoDfromWikiUser(askExtra, profile=profile, limit=limit)
        self.fromLoD(lod)
        return lod

    def fromWikiFileManager(self, wikiFileManager: WikiFileManager=None, limit:int=None) -> List[dict]:
        '''
        read me from wiki markup files using the given WikiFileManager

        Args:
            wikiFileManager(WikiFileManager): WikiFileManager to parse the wiki markup files
            limit(int): limit the amount on loaded records
        '''
        lod = self.getLoDfromWikiFileManager(wikiFileManager, limit=limit)
        self.fromLoD(lod)
        return lod


class OREvent(Event):
    '''
    I represent an Event retrieved from OPENRESEARCH

    see https://rq.bitplan.com/index.php/Event
    '''
    templateName = "Event"
    entityName = 'Event'

    propertyLookupList = [
        {'prop': 'Acronym', 'name': 'acronym', 'templateParam': "Acronym"},
        {'prop': 'End date', 'name': 'endDate', 'templateParam': "End date"},
        {'prop': 'Event in series', 'name': 'inEventSeries', 'templateParam': "Series"},
        {'prop': 'Event presence', 'name': 'presence', 'templateParam': "presence"},
        {'prop': 'Event type', 'name': 'eventType', 'templateParam': "Type"},
        {'prop': 'Has_location_country', 'name': 'country', 'templateParam': "Country"},
        {'prop': 'Has_location_state', 'name': 'region', 'templateParam': "State"},
        {'prop': 'Has_location_city', 'name': 'city', 'templateParam': "City"},
        {'prop': 'Has year', 'name': 'year', 'templateParam': "Year"},
        {'prop': 'Homepage', 'name': 'homepage', 'templateParam': "Homepage"},
        {'prop': 'Ordinal', 'name': 'ordinal', 'templateParam': "Ordinal"},
        {'prop': 'Start date', 'name': 'startDate', 'templateParam': "Start date"},
        {'prop': 'Title', 'name': 'title', 'templateParam': "Title"},
        {'prop': 'Accepted papers', 'name': 'acceptedPapers', 'templateParam': "Accepted papers"},
        {'prop': 'Submitted papers', 'name': 'submittedPapers', 'templateParam': "Submitted papers"},
        {'prop': 'presence', 'name': 'presence', 'templateParam': "presence"},
        {'prop': 'WikiCFP-ID', 'name': 'wikicfpId', 'templateParam': 'wikicfpId' },
        {'prop':'DblpConferenceId','name':'DblpConferenceId','templateParam':'DblpConferenceId'},
        {'prop': 'TibKatId', 'name': 'TibKatId', 'templateParam': 'TibKatId'},
        {'prop': 'TIBKAT-ISBN', 'name': 'ISBN', 'templateParam': 'ISBN'},
        {'prop': 'Wikidataid', 'name': 'wikidataId', 'templateParam': 'wikidataid'},
        {'prop': 'GND-ID', 'name': 'gndId', 'templateParam': 'gndId'}
    ]

    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()

    @classmethod
    def getSamples(cls):
        samplesLOD = [{
                "pageTitle": "ICSME 2020",
                "acronym": "ICSME 2020",
                "ordinal": 36,
                "eventType": "Conference",
                "startDate": datetime.fromisoformat("2020-09-27"),
                "endDate": datetime.fromisoformat("2020-09-27")
            },
            {
                "pageTitle": "WebSci 2019",
                "acronym": "WebSci 2019",
                "ordinal": 11,
                "homepage": "http://websci19.webscience.org/",
                "title": "11th ACM Conference on Web Science",
                "eventType": "Conference",
                "startDate": datetime.fromisoformat("2019-06-30"),
                "endDate": datetime.fromisoformat("2019-07-03"),
                "inEventSeries": "WebSci",
                "country": "USA",
                "region": "US-MA",
                "city": "Boston",
                "acceptedPapers": 41,
                "submittedPapers": 120,
                "presence": "online",
                "wikicfpId": 891,
                "tibKatId":"1736060724",
                "subject": "Software engineering",
                "ISBN":"9781450370707",
                "gndId":"1221636014"
            },
            {
                "acronym": "5GU 2017",
                "city": "Melbourne",
                "country": "Australia",
                "endDate": datetime.fromisoformat("2017-06-09T00:00:00"),
                "eventType": "Conference",
                "homepage": "http://5guconference.org/2017/show/cf-papers",
                "inEventSeries": "5GU",
                "ordinal": 2,
                "startDate": datetime.fromisoformat("2017-06-08T00:00:00"),
                "title": "2nd EAI International Conference on 5G for Ubiquitous Connectivity",
                # technical attributes - SMW specific
                "pageTitle": "5GU 2017",
                "lastEditor": "Wolfgang Fahl",
                "creationDate": datetime.fromisoformat("2016-09-25T07:36:02"),
                "modificationDate": datetime.fromisoformat("2020-11-05T12:33:23")
            },
            {
                'acronym': "IDC 2009",
                'title': "The 8th International Conference on Interaction Design and Children",
                'pageTitle': 'IDC 2009',
                'ordinal': 8,
                'year':2009,
                'yearStr':'2009',
                'url':'https://confident.dbis.rwth-aachen.de/or/index.php?title=IDC_2009'
            },
            {
                'acronym': "VNC 2019",
                'title': "2019 IEEE Vehicular Networking Conference (VNC)",
                'pageTitle': 'VNC 2019',
                'ordinal': 11,
                'DblpConferenceId':"vnc/vnc2019",
                'wikidataid':"Q106335329",
                'doi':'10.1109/VNC48660.2019'
            }

        ]
        return samplesLOD

    @classmethod
    def getSampleWikiTextList(cls, mode='legacy'):
        if mode == 'legacy':
            samplesWikiSon = ["""{{Event
|Acronym=ICSME 2020
|Title=36th IEEE International Conference on Software Maintenance and Evolution
|Ordinal=36
|Series=ICSME
|Type=Conference
|Field=Software engineering
|Start date=2020/09/27
|End date=2020/10/03
|Homepage=https://icsme2020.github.io/
|City=Adelaide
|presence=online
|Country=Australia
|Abstract deadline=2020/05/22
|Paper deadline=2020/05/28
|Notification=2020/08/04
|Camera ready=2020/08/25
|Has host organization=Institute of Electrical and Electronics Engineers
|Has coordinator=Sebastian Baltes
|has general chair=Christoph Treude, Hongyu Zhang
|has program chair=Kelly Blincoe, Zhenchang Xing
|has demo chair=Mario Linares Vasquez, Hailong Sun
}}''',
'''36th IEEE International Conference on Software Maintenance and Evolution (ICSME)'''""", """{{Event
|Acronym=AISB 2009
|Ordinal=36
|Title=AISB Symposium: New Frontiers in Human-Robot Interaction
|Type=Conference
|Field=Uncategorized
|Start date=2009/04/08
|End date=2009/04/09
|Submission deadline=2009/01/05
|Homepage=homepages.feis.herts.ac.uk/~comqkd/HRI-AISB2009-Symposium.html
|City=Edinburgh
|Country=United Kingdom
|Notification=2009/02/02
|Camera ready=2009/02/23
}}	
This CfP was obtained from [http://www.wikicfp.com/cfp/servlet/event.showcfp?eventid=3845&amp;copyownerid=2048 WikiCFP]
"""]
        else:
            samplesWikiSon = "..."

        return samplesWikiSon

    @classmethod
    def getPropertyLookup(cls, lookupId: str = 'prop') -> dict:
        '''
        get my PropertyLookupList as a map

        Args:
            lookupId(str): name of the lookup id

        Returns:
            dict: my mapping from wiki property names to LoD attribute Names or None if no mapping is defined
        '''
        lookup = None
        if hasattr(cls, 'propertyLookupList'):
            propertyLookupList = getattr(cls, 'propertyLookupList')
            lookup = {prop[lookupId]: prop['name'] for prop in propertyLookupList}
        return lookup

    @classmethod
    def getTemplateParamLookup(cls) -> dict:
        '''
        get my templateParam lookup list as a map
        Returns:
            dict: my mapping from templateParam names to LoD attribute Names or None if no mapping is defined
        '''
        return cls.getPropertyLookup("templateParam")

    @staticmethod
    def postProcessLodRecord(rawEvent:dict, wikiId=None, debug:bool=False):
        '''
        fix the given raw Event
        
        Args:
            rawEvent(dict): the raw event record to fix
            wikiId: wiki id of the records origin
            debug: If True display debug output
        '''
        if wikiId is not None:
            try:
                wikiUser = WikiUser.ofWikiId(wikiId)
                baseUrl=wikiUser.getWikiUrl()
                if 'pageTitle' in rawEvent:
                    pageTitle=rawEvent["pageTitle"]
                    qPageTitle=urllib.parse.quote(pageTitle)
                    url=f"{baseUrl}/index.php?title={qPageTitle}"  #ToDo: Switch to proper page url generation
                    rawEvent['url']=url
            except Exception as e:
                if debug:
                    print(f"WikiUser for {wikiId} not found:  url could not be assigned")
                    print(e)
        rawEvent['eventId']=rawEvent['pageTitle']
        if 'year' in rawEvent:
            yearStr=rawEvent['year']
            rawEvent['yearStr']=yearStr
            year = None
            try:
                year=int(yearStr)
            except Exception as _ne:
                pass
            rawEvent['year']=year
        for dateProp in ['endDate', 'startDate']:
            if dateProp in rawEvent:
                rawDateValue = rawEvent.get(dateProp)
                if isinstance(rawDateValue, str):
                    if rawDateValue:
                        try:
                            dateValue = dateutil.parser.parse(rawEvent.get(dateProp))
                            if dateValue:
                                rawEvent[dateProp] = dateValue
                        except Exception as e:
                            if debug:
                                print(f"{dateProp}: {rawDateValue} → Could not be converted to datetime (event record:{rawEvent})")
                            rawEvent[dateProp] = None
                    else:
                        rawEvent[dateProp] = None
        Ordinal.addParsedOrdinal(rawEvent)


class OREventSeriesManager(EventSeriesManager):
    '''
    i represent a list of EventSeries
    '''

    def __init__(self,
                 sourceConfig:EventDataSourceConfig=None,
                 config:StorageConfig=None,
                 wikiId:str='orclone',
                 via='api',
                 verbose:bool=False,
                 debug=False):
        '''
        construct me
        '''
        self.eventSeries = []
        super(OREventSeriesManager, self).__init__(name="OREventSeries",
                                                   sourceConfig=sourceConfig,
                                                   clazz=OREventSeries,
                                                   primaryKey="pageTitle",
                                                   config=config)
        self.wikiId = wikiId
        self.via = via
        self.debug = debug
        if self.debug:
            self.profile = True
        self.verbose=verbose
        
    def configure(self):
        '''
        configure me
        '''
        if not hasattr(self, "getListOfDicts"):
            if self.via == 'wikiMarkup':
                self.getListOfDicts = self.getLodFromWikiMarkup
            elif self.via == 'backup':
                self.getListOfDicts = self.getLoDfromWikiFileManager
            else:
                self.getListOfDicts = self.getLoDfromWikiUser

    def getLodFromWikiMarkup(self, limit:int=None) -> List[dict]:
        """
        Retrieves the event records from the WikiMarkup of the event pages.

        Args:
            limit(int): limit number of retrieved records. If None (default) retrieve all event records

        Returns:
            LoD List of event records
        """
        lod = OrSMW.getLodFromWikiMarkup(self.wikiId, OREventSeries, limit=limit)
        self.setAllAttr(lod, "source", f"{self.wikiId}-wikiMarkup")
        self.postProcessLodRecords(lod, wikiId=self.wikiId, debug=self.debug)
        return lod

    def getLoDfromWikiUser(self,askExtra:str="", profile: bool=False, limit:int=None) -> List[dict]:
        '''

        Args:
            wikiuser(WikiUser): wikiuser specifiying from which wiki to the records should be queried
            askExtra(str): additional selector for the query e.g. '[[Modification date::>=2022]]'
            profile(bool): Profile the retrieval of the records
            limit(int): limit number of queried records
        '''
        lod = OrSMW.getLodFromWikiApi(self.wikiId, OREventSeries, askExtra=askExtra, limit=limit, profile=profile)
        self.setAllAttr(lod, "source", f"{self.wikiId}")
        self.postProcessLodRecords(lod, wikiId=self.wikiId, debug=self.debug)
        return lod

    def getLoDfromWikiFileManager(self, wikiFileManager: WikiFileManager = None, limit: int = None) -> List[dict]:
        '''
        get my List of Dicts from the given WikiFileManager

        Args:
            wikiFileManager(WikiFileManager): WikiFileManager from which the records should be loaded
            limit(int): limit the amount on loaded records
        '''
        lod = OrSMW.getLodFromWikiFiles(self.wikiId, OREventSeries, wikiFileManager=wikiFileManager, limit=limit)
        self.setAllAttr(lod, "source", f"{self.wikiId}-backup")
        self.postProcessLodRecords(lod, wikiId=self.wikiId, debug=self.debug)
        return lod


    @classmethod
    def getPropertyLookup(cls) -> dict:
        '''
        get my PropertyLookupList as a map

        Returns:
            dict: my mapping from wiki property names to LoD attribute Names or None if no mapping is defined
        '''
        lookup = None
        if hasattr(OREventSeries, 'propertyLookupList'):
            propertyLookupList = OREventSeries.propertyLookupList
            lookup, _duplicates = LOD.getLookup(propertyLookupList, 'prop')
        return lookup

    def fromWikiUser(self, askExtra:str="", limit:int=None, profile:bool=False):
        '''
        read me from a wiki using the given WikiUser configuration

        Args:
            askExtra(string): Extra query selectors that should be included in the query
            limit(int): limit the amount on loaded records
            profile(bool): If true profile the query. Otherwise the query runs without tracking the time
        '''
        lod = self.getLoDfromWikiUser(askExtra, profile=profile, limit=limit)
        self.fromLoD(lod)
        return lod

    def fromWikiFileManager(self, wikiFileManager:WikiFileManager=None, limit:int=None):
        '''
        read me from wiki markup files using the given WikiFileManager

        Args:
            wikiFileManager(WikiFileManager): WikiFileManager to parse the wiki markup files
            limit(int): limit the amount on loaded records
        '''
        lod = self.getLoDfromWikiFileManager(wikiFileManager, limit=limit)
        self.fromLoD(lod)
        return lod


class OREventSeries(EventSeries):
    '''
    an event Series
    '''
    # TODO - this is the legacy templateName - make sure after / during migration
    # this is handled properly
    templateName = "Event series"
    entityName='EventSeries'

    propertyLookupList = [
        {'prop': 'EventSeries acronym', 'name': 'acronym', 'templateParam': 'Acronym'},
        {'prop': 'DblpSeries', 'name': 'dblpSeries', 'templateParam': 'DblpSeries'},
        {'prop': 'Homepage', 'name': 'homepage', 'templateParam': 'Homepage'},
        {'prop': 'Logo', 'name': 'logo', 'templateParam': 'Logo'},
        {'prop': 'Title', 'name': 'title', 'templateParam': 'Title'},
        # TODO enable and handle
        # { 'prop':'Field',      'name': 'subject'},
        {'prop': 'Wikidataid', 'name': 'wikidataId', 'templateParam': 'WikiDataId'},
        {'prop': 'WikiCfpSeries', 'name': 'wikiCfpSeries', 'templateParam': 'WikiCfpSeries'},
        {'prop': 'Period', 'name': 'period', 'templateParam': 'Period'},
        {'prop': 'Unit', 'name': 'unit', 'templateParam': 'Unit'},
        {'prop': 'Has CORE Rank', 'name': 'core2018Rank', 'templateParam': 'has CORE2018 Rank'},
        {'prop': 'GND-ID', 'name': 'gndId', 'templateParam': 'GND-ID'},
        # TODO add more fields according to
        # https://confident.dbis.rwth-aachen.de/or/index.php?title=Template:Event_series&action=edit
    ]

    def __init__(self, wikiFile:WikiFile=None):
        '''
        Constructor
        '''
        super().__init__()

    @classmethod
    def getSamples(cls):
        '''
        Returns a sample LOD of an event Series
        '''
        samplesLOD = [
            {
                'pageTitle': 'AAAI',
                'acronym': 'AAAI',
                'title': 'Conference on Artificial Intelligence',
                'homepage': 'www.aaai.org/Conferences/AAAI/aaai.php',
                'wikidataId': 'Q56682083',
                'dblpSeries': 'aaai',
                'period': 1,
                'unit': 'year',
                'logo':'Aaai-logo.jpg',
                'GND-ID':'309155-7'
            },
            {
                "acronym": "3DUI",
                "creationDate": datetime.fromisoformat("2020-03-17T22:54:10"),
                "dblpSeries": "3dui",
                "lastEditor": "Wolfgang Fahl",
                "modificationDate": datetime.fromisoformat("2021-02-13T06:56:46"),
                "pageTitle": "3DUI",
                "title": "IEEE Symposium on 3D User Interfaces",
                "period": "year",
                "unit": 1,
                "wikidataId": "Q105456162",
                'url': 'https://confident.dbis.rwth-aachen.de/or/index.php?title=3DUI',
                'WikiCfpSeries': 160,
                'core2018Rank':'B',
                'subject': 'User Interfaces',
            },
            ]
        return samplesLOD

    @classmethod
    def getSampleWikiTextList(cls, mode='legacy'):
        '''
        Returns a sample of Event Series in wikison format
        Args:
            mode(str): Default legacy, used to provide the mode dependant on updates and changes to structure of Event series
        '''
        if mode == 'legacy':
            samplesWikiSon = ["""{{Event series
|Acronym=AAAI
|Title=Conference on Artificial Intelligence
|Logo=Aaai-logo.jpg
|has CORE2017 Rank=A*
|Field=Artificial intelligence
|Period=1
|Unit=year
|Homepage=www.aaai.org/Conferences/AAAI/aaai.php
|WikiDataId=Q56682083
|has CORE2018 Rank=A*
|has Bibliography=dblp.uni-trier.de/db/conf/aaai/
|has CORE2014 Rank=A*
|DblpSeries=aaai
}}"""]
        else:
            samplesWikiSon = "..."

        return samplesWikiSon

    @staticmethod
    def postProcessLodRecord(rawEvent: dict, wikiId=None, debug:bool=False):
        '''
        fix the given raw Event

        Args:
            rawEvent(dict): the raw event record to fix
            wikiId: wiki id of the records origin
            debug: If True display debug output
        '''
        if wikiId is not None:
            try:
                wikiUser = WikiUser.ofWikiId(wikiId)
                baseUrl = wikiUser.getWikiUrl()
                if 'pageTitle' in rawEvent:
                    pageTitle = rawEvent["pageTitle"]
                    qPageTitle = urllib.parse.quote(pageTitle)
                    url = f"{baseUrl}/index.php?title={qPageTitle}"   #ToDo: Switch to proper page url generation
                    rawEvent['url'] = url
            except Exception as e:
                if debug:
                    print(f"WikiUser for {wikiId} not found:  url could not be assigned")
                    print(e)
        rawEvent['eventSeriesId'] = rawEvent['pageTitle']
        period = rawEvent.get('period')
        if period and isinstance(period, str):
            if period.isnumeric():
                rawEvent['period'] = int(period)
            else:
                del rawEvent['period']

    @classmethod
    def getPropertyLookup(cls, lookupId: str = 'prop') -> dict:
        '''
        get my PropertyLookupList as a map

        Args:
            lookupId(str): name of the lookup id

        Returns:
            dict: my mapping from wiki property names to LoD attribute Names or None if no mapping is defined
        '''
        lookup = None
        if hasattr(cls, 'propertyLookupList'):
            propertyLookupList = getattr(cls, 'propertyLookupList')
            lookup = {prop[lookupId]: prop['name'] for prop in propertyLookupList}
        return lookup

    @classmethod
    def getTemplateParamLookup(cls) -> dict:
        '''
        get my templateParam lookup list as a map
        Returns:
            dict: my mapping from templateParam names to LoD attribute Names or None if no mapping is defined
        '''
        return cls.getPropertyLookup("templateParam")


class OrSMW:
    """
    Provides different access methods to data in an openresearch wiki
    """

    @classmethod
    def getAskQuery(cls,
                    entityType:Union[Type[OREvent], Type[OREventSeries]],
                    askExtra: str = "",
                    propertyLookupList: List[dict] = None) -> str:
        '''
        get the query that will ask for all records of the given entityType and their properties

        Args:
            entityType(Union[Type[OREvent], Type[OREventSeries]]): entity type
            askExtra(str): any additional SMW ask query constraints
            propertyLookupList:  a list of dicts for propertyLookup

        Return:
            str: the SMW ask query
        '''
        if askExtra is None:
            askExtra = ''
        entityName = entityType.entityName
        selector = "IsA::%s" % entityName
        ask = f"""{{{{#ask:[[{selector}]]{askExtra}
            |mainlabel=pageTitle
            |?Creation date=creationDate
            |?Modification date=modificationDate
            |?Last editor is=lastEditor
            """
        if propertyLookupList is None:
            if hasattr(entityType, 'propertyLookupList'):
                propertyLookupList = getattr(entityType, 'propertyLookupList')
        for propertyLookup in propertyLookupList:
            propName = propertyLookup['prop']
            name = propertyLookup['name']
            ask += "|?%s=%s\n" % (propName, name)
        ask += "}}"
        return ask

    @classmethod
    def getAskQueryPageTitles(cls, entityType:Union[Type[OREvent], Type[OREventSeries]]) -> str:
        """
        get the query that will ask for all pageTitles of the given entityType. e.g. all event pageTitles
        Args:
            entityType(Union[Type[OREvent], Type[OREventSeries]]): entityType

        Returns:
            str: the SMW ask query
        """
        entityName = entityType.entityName
        ask = f"""{{{{#ask:[[IsA::{entityName}]]|mainlabel=pageTitle}}}}"""
        return ask

    @classmethod
    def getLodFromWikiMarkup(cls,
                             wikiId: str,
                             entityType:Union[Type[OREvent], Type[OREventSeries]],
                             limit: int = None,
                             profile:bool=False,
                             showProgress:bool=True) -> List[dict]:
        """
        Retrieves the event records from the WikiMarkup of the event pages.

        Args:
            wikiId: id of the wiki
            entityType: entity to retrieve
            limit(int): limit number of retrieved records. If None (default) retrieve all event records
            profile: If True measure and display the elapsed time
            showProgress: If True display progress messages

        Returns:
            LoD List of entity records
        """
        wikiPush = WikiPush(fromWikiId=wikiId)
        askQuery = cls.getAskQueryPageTitles(entityType=entityType)
        queryDivision = 10 if limit is None or limit >= 1000 else 1
        profiler = Profiler(msg=f"querying of {entityType.entityName} records from WikiMarkup", profile=profile)
        pageTitles = wikiPush.query(askQuery=askQuery, limit=limit, queryDivision=queryDivision)
        wikiPage = WikiPage(wikiId=wikiId, login=False)
        lod = []
        total = len(pageTitles)
        for i, pageTitle in enumerate(pageTitles):
            if showProgress:
                print(f"({i+1}/{total}) Extracting {entityType.templateName} record from {pageTitle} ...", end=' ')
            try:
                record = wikiPage.getWikiSonFromPage(pageTitle, entityType.templateName, includeWikiMarkup=True)
                record = cls.normalizeProperties(record, entityType, force=False, includeProps=['pageTitle', 'wikiMarkup'])
                record['pageTitle'] = pageTitle
                lod.append(record)
                if showProgress:
                    print('✅')
            except Exception as e:
                if showProgress:
                    print('❌')
        profiler.time()
        return lod

    @classmethod
    def getLodFromWikiApi(cls,
                          wikiId:str,
                          entityType:Union[Type[OREvent], Type[OREventSeries]],
                          askExtra:str=None,
                          limit:int=None,
                          profile:bool=False) -> List[dict]:
        """
        Retrieves the event records from the SMW api by querying it for all entity properties.

        Args:
            wikiId: id of the wiki
            entityType: entity to retrieve
            askExtra: extra ask query selector to include in the query
            limit: limit number of retrieved records. If None (default) retrieve all event records
            profile: If True measure and display the elapsed time

        Returns:
            LoD: List of entity records
        """
        wikiPush = WikiPush(fromWikiId=wikiId)
        askQuery = cls.getAskQuery(entityType=entityType, askExtra=askExtra)
        queryDivision = 10 if limit is None or limit >= 1000 else 1
        profiler = Profiler(msg=f"querying of {entityType.entityName} records over SMW api", profile=profile)
        records = wikiPush.formatQueryResult(askQuery, limit=limit, queryDivision=queryDivision)
        profiler.time()
        return records

    @classmethod
    def getLodFromWikiFiles(cls,
                          wikiId: str,
                          entityType: Union[Type[OREvent], Type[OREventSeries]],
                          wikiFileManager: WikiFileManager = None,
                          limit: int = None,
                          profile: bool = False) -> List[dict]:
        """
        Retrieves the event records from the local wikiFiles. The entity records are parsed from the WikiMarkup in the
        WikiFiles.

        Args:
            wikiId: id of the wiki
            entityType: entity to retrieve
            wikiFileManager: wikiFileManager to use. If None the default wikibackup location (~/.or/wikibackup/<wikiId>) will be used
            limit: limit number of retrieved records. If None (default) retrieve all event records
            profile: If True measure and display the elapsed time

        Returns:
            LoD: List of entity records
        """
        profiler = Profiler(msg=f"querying of {entityType.entityName} records over SMW api", profile=profile)
        if wikiFileManager is None:
            wikiTextPath = f"{Path.home()}/.or/wikibackup/{wikiId}"
            wikiFileManager = WikiFileManager(sourceWikiId=wikiId, wikiTextPath=wikiTextPath, login=False)
        wikiFileDict = wikiFileManager.getAllWikiFiles()
        lod = wikiFileManager.convertWikiFilesToLOD(wikiFiles=list(wikiFileDict.values()),
                                                    templateName=entityType.templateName,
                                                    limit=limit)
        for i, record in enumerate(lod):
            pageTitle = record.get("pageTitle")
            record = cls.normalizeProperties(record, entityType, force=False)
            record['pageTitle'] = pageTitle
            wikiFile = wikiFileDict.get(pageTitle)
            if isinstance(wikiFile, WikiFile):
                # ToDo: Decide whether the wikiMarkup is still required since it can now an event record can directly be queried from the wiki, sync problems should be neglectable
                record["wikiMarkup"] = wikiFile.wikiText
            lod[i]=record
        profiler.time()
        return lod

    @staticmethod
    def normalizeProperties(record: dict,
                            entity: Union[Type[OREvent], Type[OREventSeries]],
                            reverse: bool = False,
                            force: bool = False,
                            includeProps:list=None,
                            debug: bool = False) -> dict:
        """
        update the keys of the given record. If reverse is False normalize the given keys with the property map provided
        by the given entity. If reverse is True denormalize the keys back to the template params.

        Normalize: Acronym (template param) -> acronym (normalized param)
        Denormalize: acronym (normalized param) -> Acronym (template param)

        Args:
            record(dict): record to normalize
            entity: entity containing the template property mapping
            reverse(bool): If False normalize. Otherwise, denormalize back to template property names
            force(bool): If True include properties that are not present in the getTemplateParamLookup() of the given
                         entity. Otherwise, exclude these properties and show a warning.
            includeProps(list): List of properties that should be included even if not in getTemplateParamLookup()
            debug(bool): If True show debug messages.

        Returns:
            dict
        """
        if includeProps is None:
            includeProps = []
        propMap = entity.getTemplateParamLookup()
        if reverse:
            propMap = {v: k for k, v in propMap.items()}
        res = {}
        for key, value in record.items():
            if key in propMap:
                res[propMap[key]] = value
            else:
                if force or key in includeProps:
                    res[key] = value
                else:
                    msg = f"Property '{key}' will be excluded (not present in the getTemplateParamLookup() of {entity.__name__}). To include this property use force=True"
                    if debug:
                        print(msg)
        return res