from datetime import datetime

import dateutil.parser
from lodstorage.lod import LOD
from lodstorage.storageconfig import StorageConfig
from wikibot.wikiuser import WikiUser
from wikifile.wikiFile import WikiFile
from wikifile.wikiFileManager import WikiFileManager

from corpus.event import Event, EventSeries, EventSeriesManager, EventManager
from corpus.eventcorpus import EventDataSource,EventDataSourceConfig
from ptp.ordinal import Ordinal
from corpus.smw.topic import SMWEntity, SMWEntityList
import urllib

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
        lookupId=f"{wikiId}" if via=="api" else f"{wikiId}-{via}"
        tableSuffix=f"{wikiId}" if via=="api" else f"{wikiId}{via}" 
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
            url='https://www.openresearch.org/wiki/Main_Page' if wikiId=="or" else "https://confident.dbis.rwth-aachen.de/or/index.php?title=Main_Page"
        sourceConfig=EventDataSourceConfig(lookupId=lookupId,name=name,url=url,title=title,tableSuffix=tableSuffix,locationAttribute='location')
        super().__init__(OREventManager(sourceConfig=sourceConfig),OREventSeriesManager(sourceConfig=sourceConfig),sourceConfig)

class OREventManager(EventManager):
    '''
    Manager for OpenResearch Events
    
    see https://www.openresearch.org
    '''

    def __init__(self,sourceConfig:EventDataSourceConfig=None,config:StorageConfig=None, verbose:bool=False, debug=False):
        '''
        Constructor
        '''
        self.events=[]
        super().__init__(name="OREvents",sourceConfig=sourceConfig,
                                             clazz=OREvent,
                                             primaryKey="pageTitle",
                                             config=config)
        self.smwHandler=SMWEntityList(self)
        self.debug=debug
        self.verbose=verbose
        if self.debug:
            self.profile = True
    
    def configure(self):
        '''
        configure me
        '''
        if not hasattr(self, "getListOfDicts"):
            if self.wikiFileManager:
                self.getListOfDicts=self.getLoDfromWikiFileManager
            if hasattr(self,'wikiUser'):
                self.getListOfDicts=self.getLoDfromWikiUser

    @property
    def wikiFileManager(self):
        return self.smwHandler.wikiFileManager

    @wikiFileManager.setter
    def wikiFileManager(self, wikiFileManager:WikiFileManager):
        self.smwHandler.wikiFileManager=wikiFileManager

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

    def fromWikiUser(self, wikiuser: WikiUser, askExtra: str = "", profile: bool = False):
        '''
        read me from a wiki using the given WikiUser configuration

        Args:
            wikiuser(wikiuser): wikiuser and thus the wiki that should be queried for the its EventSeries
            askExtra(string): Extra query selectors that should be included in the query
            profile(bool): If true profile the query. Otherwise the query runs without tracking the time
        '''
        self.smwHandler.fromWiki(wikiuser, askExtra, profile)

    def fromWikiFileManager(self, wikiFileManager: WikiFileManager):
        '''
        read me from wiki markup files using the given WikiFileManager

        Args:
            wikiFileManager(WikiFileManager): WikiFileManager to parse the wiki markup files
        '''
        self.smwHandler.fromWikiFileManager(wikiFileManager)

    def getLoDfromWikiUser(self, wikiuser:WikiUser=None, askExtra:str="", profile:bool=False, limit:int=None):
        '''

        Args:
            wikiuser(WikiUser):
            askExtra(str):
            profile(bool):
        '''
        if limit is None:
            limit = OR.limitFiles
        if wikiuser is None and hasattr(self,'wikiUser'):
            wikiuser=self.wikiUser
        lod=self.smwHandler.getLoDfromWiki(wikiuser,askExtra,profile, limit)
        self.setAllAttr(lod,"source",f"{wikiuser.wikiId}-api")
        self.postProcessLodRecords(lod,wikiUser=wikiuser)
        return lod

    def getLoDfromWikiFileManager(self, wikiFileManager:WikiFileManager=None, limit:int=None):
        '''
        get my list of dicts from the given WikiFileManager

        Args:
            wikiFileManager(WikiFileManager): WikiFileManager from which the records should be loaded
            limit(int): limit the amount on loaded records
        '''
        if limit is None:
            limit = OR.limitFiles
        if self.wikiFileManager:
            wikiFileManager=self.wikiFileManager
        lod=self.smwHandler.getLoDfromWikiFileManager(wikiFileManager, limit=limit)
        LOD.setNone4List(lod, LOD.getFields(self.clazz.getSamples()))
        # TODO set source more specific
        self.setAllAttr(lod,"source","or")
        wikiUser=None
        if wikiFileManager.wikiPush.fromWiki:
            if wikiFileManager.wikiPush.fromWiki.wikiUser:
                wikiUser=wikiFileManager.wikiPush.fromWiki.wikiUser
        self.postProcessLodRecords(lod,wikiUser=wikiUser)
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
        {'prop': 'wikicfpId', 'name': 'wikicfpId', 'templateParam': 'wikicfpId' },
        {'prop':'DblpConferenceId','name':'DblpConferenceId','templateParam':'DblpConferenceId'},
        {'prop': 'TibKatId', 'name': 'TibKatId', 'templateParam': 'TibKatId'},
        {'prop': 'TIBKAT-ISBN', 'name': 'ISBN', 'templateParam': 'ISBN'},
        {'prop': 'Wikidataid', 'name': 'wikidataId', 'templateParam': 'wikidataid'}
    ]

    def __init__(self, wikiFile:WikiFile=None):
        '''
        Constructor
        '''
        super().__init__()
        self.smwHandler=SMWEntity(self, wikiFile)

    @property
    def wikiFile(self):
        return self.smwHandler.wikiFile

    @wikiFile.setter
    def wikiFile(self, wikiFile: WikiFile):
        self.smwHandler.wikiFile = wikiFile


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
                "ordinal": 10,
                "homepage": "http://websci19.webscience.org/",
                "title": "10th ACM Conference on Web Science",
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
                "ISBN":"9781450370707"
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
    def postProcessLodRecord(rawEvent:dict,wikiUser=None):
        '''
        fix the given raw Event
        
        Args:
            rawEvent(dict): the raw event record to fix
        '''
        if wikiUser is not None:
            baseUrl=wikiUser.getWikiUrl()
            if 'pageTitle' in rawEvent:
                pageTitle=rawEvent["pageTitle"]
                qPageTitle=urllib.parse.quote(pageTitle)
                url=f"{baseUrl}/index.php?title={qPageTitle}"
                rawEvent['url']=url
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
                            print(f"{dateProp}: {rawDateValue} → Could not be converted to datetime (event record:{rawEvent})")
                            rawEvent[dateProp] = None
                    else:
                        rawEvent[dateProp] = None
        Ordinal.addParsedOrdinal(rawEvent)

class OREventSeriesManager(EventSeriesManager):
    '''
    i represent a list of EventSeries
    '''

    def __init__(self,sourceConfig:EventDataSourceConfig=None,config:StorageConfig=None, verbose:bool=False, debug=False):
        '''
        construct me
        '''
        self.eventSeries = []
        super(OREventSeriesManager, self).__init__(name="OREventSeries",
                                                   sourceConfig=sourceConfig,
                                                   clazz=OREventSeries,
                                                   primaryKey="pageTitle",
                                                   config=config)
        # delegate smw functionality
        self.smwHandler=SMWEntityList(self)
        self.debug = debug
        if self.debug:
            self.profile = True
        self.verbose=verbose
        
    def configure(self):
        '''
        configure me
        '''
        if not hasattr(self, "getListOfDicts"):
            if self.wikiFileManager:
                self.getListOfDicts=self.getLoDfromWikiFileManager  
            if hasattr(self,'wikiUser'):
                self.getListOfDicts=self.getLoDfromWikiUser               

    @property
    def wikiFileManager(self):
        return self.smwHandler.wikiFileManager

    @wikiFileManager.setter
    def wikiFileManager(self, wikiFileManager: WikiFileManager):
        self.smwHandler.wikiFileManager = wikiFileManager

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

    def fromWikiUser(self, wikiuser:WikiUser, askExtra:str="", profile:bool=False):
        '''
        read me from a wiki using the given WikiUser configuration

        Args:
            wikiuser(wikiuser): wikiuser and thus the wiki that should be queried for the its EventSeries
            askExtra(string): Extra query selectors that should be included in the query
            profile(bool): If true profile the query. Otherwise the query runs without tracking the time
        '''
        self.smwHandler.fromWiki(wikiuser,askExtra,profile)

    def fromWikiFileManager(self, wikiFileManager:WikiFileManager):
        '''
        read me from wiki markup files using the given WikiFileManager

        Args:
            wikiFileManager(WikiFileManager): WikiFileManager to parse the wiki markup files
        '''
        self.smwHandler.fromWikiFileManager(wikiFileManager)

    def getLoDfromWikiUser(self, wikiuser:WikiUser=None, askExtra:str="", profile:bool=False, limit:int=None):
        '''

        Args:
            wikiuser(WikiUser): wikiuser specifiying from which wiki to the records should be queried
            askExtra(str): additional selector for the query e.g. '[[Modification date::>=2022]]'
            profile(bool):
            limit(int): limit number of queried records
        '''
        if limit is None:
            limit = OR.limitFiles
        if wikiuser is None and hasattr(self,'wikiUser'):
            wikiuser=self.wikiUser
        lod=self.smwHandler.getLoDfromWiki(wikiuser,askExtra,profile, limit=limit)
        self.setAllAttr(lod,"source",f"{wikiuser.wikiId}-api")
        self.postProcessLodRecords(lod, wikiUser=wikiuser)
        return lod

    def getLoDfromWikiFileManager(self, wikiFileManager:WikiFileManager=None, limit:int=None):
        '''
        get my List of Dicts from the given WikiFileManager
        
        Args:
            wikiFileManager(WikiFileManager): WikiFileManager from which the records should be loaded
            limit(int): limit the amount on loaded records
        '''
        if limit is None:
            limit = OR.limitFiles
        if self.wikiFileManager:
            wikiFileManager=self.wikiFileManager
        lod=self.smwHandler.getLoDfromWikiFileManager(wikiFileManager, limit=limit)
        LOD.setNone4List(lod, LOD.getFields(self.clazz.getSamples()))
        self.setAllAttr(lod,"source",f"{wikiFileManager.wikiUser.wikiId}-backup")
        wikiUser=None
        if wikiFileManager.wikiPush.fromWiki:
            if wikiFileManager.wikiPush.fromWiki.wikiUser:
                wikiUser=wikiFileManager.wikiPush.fromWiki.wikiUser
        self.postProcessLodRecords(lod, wikiUser=wikiUser)
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
        # TODO add more fields according to
        # https://confident.dbis.rwth-aachen.de/or/index.php?title=Template:Event_series&action=edit
    ]

    def __init__(self, wikiFile:WikiFile=None):
        '''
        Constructor
        '''
        super().__init__()
        self.smwHandler=SMWEntity(self, wikiFile)

    @property
    def wikiFile(self):
        return self.smwHandler.wikiFile

    @wikiFile.setter
    def wikiFile(self, wikiFile:WikiFile):
        self.smwHandler.wikiFile=wikiFile

    @classmethod
    def getSamples(self):
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
                'logo':'Aaai-logo.jpg'
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
    def postProcessLodRecord(rawEvent: dict, wikiUser=None):
        '''
        fix the given raw Event

        Args:
            rawEvent(dict): the raw event record to fix
        '''
        if wikiUser is not None:
            baseUrl = wikiUser.getWikiUrl()
            if 'pageTitle' in rawEvent:
                pageTitle = rawEvent["pageTitle"]
                qPageTitle = urllib.parse.quote(pageTitle)
                url = f"{baseUrl}/index.php?title={qPageTitle}"
                rawEvent['url'] = url
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