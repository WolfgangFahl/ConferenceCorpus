'''
Created on 2021-07-26

@author: wf
'''
from typing import Callable
from corpus.config import EventDataSourceConfig
from lodstorage.csv import CSV
from lodstorage.entity import EntityManager
from lodstorage.jsonable import JSONAble
from lodstorage.lod import LOD
from lodstorage.sql import SQLDB
from corpus.utils.download import Profiler
from lodstorage.storageconfig import StorageConfig
from corpus.quality.rating import RatingManager
from corpus.eventrating import EventRating,EventSeriesRating
from lodstorage.sparql import SPARQL
from lodstorage.schema import Schema
from lodstorage.query import QueryManager
import os
import sys

import re
class EventStorage:
    '''
    common storage aspects of the EventManager and EventSeriesManager
    '''
    profile=True
    withShowProgress=False
    viewTableExcludes={
            "event":
                ["event_acm",
                 "event_ceurws"
                 "event_orclonebackup",
                 "event_or",
                 "event_orbackup"],
            "eventseries":
                ["eventseries_acm",
                 "eventseries_or",
                 "eventseries_orbackup",
                 "eventseries_orclonebackup",
                 "eventseries_gnd"]
            }
    
    @staticmethod
    def getStorageConfig(debug:bool=False,mode='sql')->StorageConfig:
        '''
        get the storageConfiguration
        
        Args:
            debug(bool): if True show debug information
            mode(str): sql or json
        
        Return:
            StorageConfig: the storage configuration to be used
        '''
        if mode=='sql':
            config=StorageConfig.getSQL(debug=debug)
        elif mode=='json':
            config=StorageConfig.getJSON()
        elif mode=='jsonpickle':
            config=StorageConfig.getJsonPickle(debug=debug)
        else:
            raise Exception(f"invalid mode {mode}")
        config.cacheDirName="conferencecorpus"
        cachedir=config.getCachePath() 
        config.profile=EventStorage.profile
        config.withShowProgress=EventStorage.withShowProgress
        if mode=='sql':
            config.cacheFile=f"{cachedir}/EventCorpus.db"
        return config
    
    @classmethod
    def getQueryManager(cls,lang='sql',name="queries",debug=False):
        '''
        get the query manager for the given language and fileName
        
        Args:
            lang(str): the language of the queries to extract
            name(str): the name of the manager containing the query specifications
            debug(bool): if True set debugging on
        '''
        cachedir=EventStorage.getStorageConfig().getCachePath()
        for path in cachedir,os.path.dirname(__file__)+"/../resources":
            qYamlFile=f"{path}/{name}.yaml"
            if os.path.isfile(qYamlFile):
                qm=QueryManager(lang=lang,debug=debug,queriesPath=qYamlFile)
                return qm
        return None
    
    @classmethod
    def getDBFile(cls,cacheFileName="EventCorpus"):
        '''
        get the database file for the given cacheFileName
        
        Args:
            cacheFileName(str): the name of the cacheFile without suffix
        '''
        config=cls.getStorageConfig()
        cachedir=config.getCachePath()
        dbfile=f"{cachedir}/{cacheFileName}.db"
        dbfile=os.path.abspath(dbfile)
        return dbfile
    
    @classmethod
    def getSqlDB(cls):
        '''
        get the SQL Database
        '''
        dbfile=EventStorage.getDBFile()
        sqlDB=SQLDB(dbfile)
        return sqlDB
    
    @classmethod
    def getTableList(cls,withInstanceCount:bool=True)->list:
        '''
        get the list of SQL Tables involved
        
        Return:
            list: the map of SQL tables used for caching
            withInstanceCount(bool): if TRUE add the count of instances to the table Map 
        '''
        sqlDB=EventStorage.getSqlDB()
        tableList=sqlDB.getTableList()
        for table in tableList:
            tableName=table["name"]
            if withInstanceCount:
                countQuery="SELECT count(*) as count from %s" % tableName
                countResult=sqlDB.query(countQuery)
                table['instances']=countResult[0]['count']
        return tableList
    
    @classmethod
    def getViewTableList(cls,viewName,exclude=None):
        sqlDB=EventStorage.getSqlDB()
        tableList=sqlDB.getTableList()  
        viewTableList=[]
        for table in tableList:
            tableName=table["name"]
            if tableName.startswith(f"{viewName}_"):
                if exclude is None or tableName not in exclude[viewName]:
                    viewTableList.append(table)
        return viewTableList
    
    @classmethod
    def getCommonViewDDLs(cls,viewNames=["event","eventseries"],exclude=None):
        '''
        get the SQL DDL for a common view 
        
        Return:
            str: the SQL DDL CREATE VIEW command
        '''
           
        viewDDLs={}
        for viewName in viewNames:
            viewTableList=cls.getViewTableList(viewName, exclude=exclude)
            viewDDL=Schema.getGeneralViewDDL(viewTableList, viewName)
            viewDDLs[viewName]=viewDDL
        return viewDDLs
        
    @classmethod
    def createViews(cls,exclude=None):
        ''' 
          create the general Event view
          
        Args:
            cacheFileName(string): the path to the database
        '''
        sqlDB=EventStorage.getSqlDB()
        viewDDLs=EventStorage.getCommonViewDDLs(exclude=exclude)
        for viewName,viewDDL in viewDDLs.items():
            sqlDB.c.execute(f"DROP VIEW IF EXISTS {viewName}")
            sqlDB.c.execute(viewDDL)
    

class Event(JSONAble):
    '''
    base class for Event entities
    '''
    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()

    def __str__(self):
        '''
        return my string representation
        
        Return:
            str: the string representation
        '''
        text=self.__class__.__name__
        attrs=["pageTitle","acronym","eventId","title","year","source","url"]
        delim=":"
        for attr in attrs:
            if hasattr(self, attr):
                value=getattr(self,attr)
                text+=f"{delim}{value}"
                delim=":" 
        return text
    
    def getLookupAcronym(self):
        ''' 
            get the lookup acronym of this event e.g. add year information 
            
        Return:
            str: the acronym to be used for lookup operations
        '''
        if hasattr(self,'acronym') and self.acronym is not None:
            self.lookupAcronym=self.acronym
        else:
            if hasattr(self,'event'):
                self.lookupAcronym=self.event
        if hasattr(self,'lookupAcronym'):
            if self.lookupAcronym is not None:
                try:
                    if hasattr(self, 'year') and self.year is not None and not re.search(r'[0-9]{4}',self.lookupAcronym):
                        self.lookupAcronym="%s %s" % (self.lookupAcronym,str(self.year))
                except TypeError as te:
                    print ('Warning getLookupAcronym failed for year: %s and lookupAcronym %s' % (self.year,self.lookupAcronym))   
    

    def getRecord(self):
        '''
        get my dict elements that are defined in getSamples
        
        Return:
            dict: fields of my __dict__ which are defined in getSamples
        '''
        fields = None
        if hasattr(self, 'getSamples') and callable(getattr(self, 'getSamples')):
            fields = LOD.getFields(self.getSamples())
        record = {}
        recordDict= self.__dict__
        for field in fields:
            if field in recordDict:
                record[field] = recordDict[field]
        return record
    
    def mapFromDict(self,d:dict,maptuples):
        '''
        set my attributes from the given dict mapping with the given
        mapping (key->attr) tuples
        
        Args:
            d(dict): the dictionary to map
            maptuples(list): the list of tuples for mapping
        '''
        for key,attr in maptuples:
            if key in d:
                setattr(self,attr,d[key])

    def asWikiMarkup(self,series:str,templateParamLookup:dict)->str:
        '''
        Args:
            series(str): the name of the series
            templateParamLookup(dict): the mapping of python attributes to Mediawiki template parameters to be used
        
        Return:
            str: my WikiMarkup
        '''
        nameValues={}
        delim=""
        for wikiName,attrName in templateParamLookup.items():
            if hasattr(self, attrName):
                value=getattr(self,attrName)
                nameValues[wikiName]=value
                
        markup=""
        nameValues["Series"]=series.upper()
        dblpConferenceId=re.sub(r"^https:\/\/dblp.org\/db\/conf\/","",self.url)
        dblpConferenceId=dblpConferenceId.replace(".html","")
        nameValues["DblpConferenceId"]=dblpConferenceId
        for name,value in nameValues.items():
            markup=f"{markup}{delim}|{name}={value}"
            delim="\n"
        markup=f"""{{{{Event
{markup}
}}}}"""
#|Type=Symposium

#|Submission deadline=2019/09/03
#|Homepage=http://ieeevr.org/2020/
#|City=Atlanta
#|Country=USA
#}}
        return markup
    
class EventSeries(JSONAble):
    '''
    base class for Event Series entities
    '''
    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()
        
    def __str__(self):
        '''
        return my
        '''
        text=self.__class__.__name__
        attrs=["pageTitle","acronym","eventSeriesId","title","source","url"]
        delim=":"
        for attr in attrs:
            if hasattr(self, attr):
                value=getattr(self,attr)
                text+=f"{delim}{value}"
                delim=":" 
        return text
    
    def asWikiMarkup(self)->str:
        '''
        convert me to wikimarkup
        
        see https://github.com/WolfgangFahl/ConferenceCorpus/issues/10
        '''
        #dblpPid=self.DBLP_pid
        #if dblpPid:
        #    dblpPid=dblpPid.replace("conf/","")
        # |WikiDataId=
        #|Title={self.title}
        #|Homepage={self.homepage}
        markup=f"""{{{{Event series
|Acronym={self.acronym}
|DblpSeries={self.eventSeriesId}
}}}}"""
        #
        return markup


class EventBaseManager(EntityManager):
    '''
    common entity Manager for ConferenceCorpus
    '''
    
    def __init__(self,name,entityName,entityPluralName:str,listName:str=None,clazz=None,sourceConfig:EventDataSourceConfig=None,primaryKey:str=None,config=None,handleInvalidListTypes=False,filterInvalidListTypes=False,debug=False,profile=True):
        '''
        Constructor
        
        Args:
            name(string): name of this eventManager
            entityName(string): entityType to be managed e.g. Country
            entityPluralName(string): plural of the the entityType e.g. Countries
            config(StorageConfig): the configuration to be used if None a default configuration will be used
            handleInvalidListTypes(bool): True if invalidListTypes should be converted or filtered
            filterInvalidListTypes(bool): True if invalidListTypes should be deleted
            debug(boolean): override debug setting when default of config is used via config=None
            profile(boolean): True if profiling/timing information should be shown for long-running operations
        '''
        self.profile=profile
        if config is None:
            config=EventStorage.getStorageConfig(debug=debug)
            self.profile=config.profile
        if sourceConfig is not None:
            tableName=sourceConfig.getTableName(entityName)
        else:
            tableName=entityName
        super().__init__(name, entityName, entityPluralName, listName, clazz, tableName, primaryKey, config, handleInvalidListTypes, filterInvalidListTypes, listSeparator='⇹',debug=debug)
   
        
    def configure(self):
        '''
        configure me - abstract method that needs to be overridden
        '''    
        raise Exception(f"specialized configure for {self.name} needs to be implemented")
 
    def setAllAttr(self,listOfDicts,attr,value):
        '''
        set all attribute values of the given attr in the given list of Dict to the given value 
        '''
        for record in listOfDicts:
            record[attr]=value
            
    def rateAll(self,ratingManager:RatingManager):
        '''
        rate all events and series based on the given rating Manager
        '''
        for entity in self.getList():
            if hasattr(entity,"rate") and callable(entity.rate):
                if isinstance(entity,Event):
                    rating=EventRating(entity)
                elif isinstance(entity,EventSeries):
                    rating=EventSeriesRating(entity)
                else:
                    raise Exception(f"rateAll for unknown entity type {type(entity).__name__}")
                entity.rate(rating)
                ratingManager.ratings.append(rating)
            
    def fromCsv(self, csvString, separator:str= ',', overwriteEvents:bool = True, updateEntitiesCallback:Callable =None):
        """

        Args:
            csvString: csvString having all the csv content
            separator: the separator of the csv
            append: to append to the self object.
            updateEntitiesCallback:

        Returns: Nothing. The self object is upadated

        """
        fields= None
        # limit csv fields to the fields defined in the samples
        if hasattr(self.clazz, 'getSamples') and callable(getattr(self.clazz, 'getSamples')):
            fields = LOD.getFields(self.clazz.getSamples())
        eventRecords= CSV.fromCSV(csvString=csvString,fields=None,delimiter=separator)
        self.updateFromLod(eventRecords, overwriteEvents=overwriteEvents, updateEntitiesCallback=updateEntitiesCallback)

    def updateFromLod(self, lod:list, overwriteEvents:bool = True, updateEntitiesCallback:Callable=None, restrictToSamples:bool=True):
        """
        Updates the entities from the given LoD. If a entity does not already exist a new one will be added.
        Args:
            lod: data to update the entities
            overwriteEvents: If False only missing values are added
            updateEntitiesCallback: Callback function that is called on an updated entity
            restrictToSamples(bool): If True only properties that are names in the samples are set.

        Returns:

        """
        originalEventsLookup = self.getLookup(attrName=self.primaryKey)[0]
        for eventRecord in lod:
            if self.primaryKey in eventRecord:
                eventRecordPrimaryKey = eventRecord.get(self.primaryKey)
                if eventRecordPrimaryKey in originalEventsLookup:
                    originalEvent = originalEventsLookup[eventRecordPrimaryKey]
                    if hasattr(originalEvent, self.primaryKey):
                        sampleProperties = []
                        if hasattr(originalEvent, 'getSamples') and callable(originalEvent.getSamples):
                            sampleProperties = LOD.getFields(originalEvent.getSamples())
                        for key, value in eventRecord.items():
                            if hasattr(originalEvent, key):
                                setattr(originalEvent, key, value)
                            else:
                                if restrictToSamples or key in sampleProperties:
                                    setattr(originalEvent, key, value)
                                else:
                                    pass
                        if updateEntitiesCallback is not None and callable(updateEntitiesCallback):
                            updateEntitiesCallback(originalEvent, overwrite=overwriteEvents)
                else:
                    self.fromLoD(lod=[eventRecord], append=True, debug=self.debug)
                    # new entity was addded → update lookup
                    originalEventsLookup = self.getLookup(attrName=self.primaryKey)[0]
                    originalEvent = originalEventsLookup[eventRecordPrimaryKey]
                    if updateEntitiesCallback is not None and callable(updateEntitiesCallback):
                        updateEntitiesCallback(originalEvent, overwrite=overwriteEvents)

    def fromCache(self,force:bool=False,getListOfDicts=None,append=False,sampleRecordCount=-1):
        '''
        overwritten version of fromCache that calls postProcessEntityList
        '''
        needsUpdate=not self.isCached() or force
        super().fromCache(force, getListOfDicts, append, sampleRecordCount)
        if needsUpdate:
            # TODO
            # this is inefficient and uses 2x the memory 
            # try postProcessing on lod instead
            self.postProcessEntityList(debug=self.debug)
            self.store()
            
    def postProcessEntityList(self,debug:bool=False):
        '''
        postProcess my entities
        '''
        # override this method
        pass
        
    def asCsv(self, separator:str=',', selectorCallback:Callable=None):
        """
        Converts the events to csv format
        Args:
            separator(str): character separating the row values
            selectorCallback: callback functions returning events to be converted to csv. If None all events are converted.

        Returns:
            csv string of events
        """
        events=self.getList()
        if selectorCallback is not None and callable(selectorCallback):
            events=selectorCallback()
            if events and type(events) != list:
                events=[events]
        fields=None
        # limit csv fields to the fields defined in the samples
        if hasattr(self.clazz, 'getSamples') and callable(getattr(self.clazz, 'getSamples')):
            fields=LOD.getFields(self.clazz.getSamples())
        if events:
            csvString=CSV.toCSV(events, includeFields=fields, delimiter=separator)
            return csvString
        return None
    
    def postProcessLodRecords(self,listOfDicts:list,**kwArgs):
        '''
        post process the given list of Dicts with raw Events
        
        Args: 
            listOfDicts(list): the list of raw Events to fix
        '''
        if hasattr(self.clazz,"postProcessLodRecord") and callable(self.clazz.postProcessLodRecord): 
            for rawEvent in listOfDicts:
                self.clazz.postProcessLodRecord(rawEvent,**kwArgs)    
                
    def getLoDfromEndpoint(self)->list:
        '''
        get my content from my endpoint
        
        Returns:
            list: the list of dicts derived from the given SPARQL query
        '''
        sparql=SPARQL(self.endpoint)
        query=self.getSparqlQuery()
        try:
            profiler=Profiler(f"SPARQL query to {self.endpoint}",profile=False)
            listOfDicts=sparql.queryAsListOfDicts(query)
        except Exception as ex:
            # handle any Exception - e.g. there might be a syntax error in the query or the
            # endpoint might not be able to handle it - the endpoint might not be available
            # or there might be a timeout
            msg=f"SPARQL query failed\nquery:\n{query}"
            profiler.profile=True
            profiler.time()
            print(msg,file=sys.stderr)
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            exmessage = template.format(type(ex).__name__, ex.args)
            print(exmessage,file=sys.stderr)
            raise(ex)
        self.postProcessLodRecords(listOfDicts)
        self.setAllAttr(listOfDicts,"source",self.source)
        return listOfDicts

    def getEventByKey(self, keyToSearch, keytype='pageTitle'):
        for event in self.getList():
            if hasattr(event, keytype):
                if getattr(event, keytype) == keyToSearch:
                    return event
            else:
                raise ValueError("Invalid keytype given")


class EventSeriesManager(EventBaseManager):
    '''
    Event series list
    '''
    def __init__(self,name:str,sourceConfig:EventDataSourceConfig=None,clazz=None,primaryKey:str=None,config:StorageConfig=None,debug=False):
        '''
        constructor 
        '''
        super().__init__(name=name,entityName="EventSeries",entityPluralName="EventSeries",primaryKey=primaryKey,listName="series",clazz=clazz,sourceConfig=sourceConfig,handleInvalidListTypes=True,config=config,debug=debug) 
            
class EventManager(EventBaseManager):
    '''
    Event entity list
    '''
    
    def __init__(self,name:str,sourceConfig:EventDataSourceConfig=None,clazz=None,primaryKey:str=None,config:StorageConfig=None,debug=False):
        '''
        constructor 
        '''
        super(EventManager, self).__init__(name=name,entityName="Event",entityPluralName="Events",primaryKey=primaryKey,listName="events",clazz=clazz,sourceConfig=sourceConfig,config=config,handleInvalidListTypes=True,debug=debug,profile=config.profile if config else False)
        
 
    def linkSeriesAndEvent(self, eventSeriesManager:EventSeriesManager, seriesKey:str="series"):
        '''
        link Series and Event using the given foreignKey

        Args:
            seriesKey(str): the key to be use for lookup
            eventSeriesManager(EventSeriesManager):
        '''
        # get foreign key hashtable
        self.seriesLookup = LOD.getLookup(self.getList(), seriesKey, withDuplicates=True)
        # get "primary" key hashtable
        self.seriesAcronymLookup = LOD.getLookup(eventSeriesManager.getList(), "acronym", withDuplicates=True)

        for seriesAcronym in self.seriesLookup.keys():
            if seriesAcronym in self.seriesAcronymLookup:
                seriesEvents = self.seriesLookup[seriesAcronym]
                if hasattr(self, 'verbose') and self.verbose:
                    print(f"{seriesAcronym}:{len(seriesEvents):4d}")
            else:
                if self.debug:
                    print(f"Event Series Acronym {seriesAcronym} lookup failed")
        if self.debug:
            print("%d events/%d eventSeries -> %d linked" % (
            len(self.getList()), len(eventSeriesManager.getList()), len(self.seriesLookup)))
            
    def getEventsInSeries(self,seriesAcronym):
        """
        Return all the events in a given series.
        """
        if seriesAcronym in self.seriesLookup:
            seriesEvents = self.seriesLookup[seriesAcronym]
            if self.debug:
                print(f"{seriesAcronym}:{len(seriesEvents):4d}")
        else:
            if self.debug:
                print(f"Event Series Acronym {seriesAcronym} lookup failed - Series not known")
            return None
        return seriesEvents
    
    @staticmethod
    def asWikiSon(eventDicts):  
        wikison=""
        for eventDict in eventDicts:
            wikison+=EventManager.eventDictToWikiSon(eventDict)
        return wikison
    
    @staticmethod
    def eventDictToWikiSon(eventDict):
        wikison="{{Event\n"
        for key,value in eventDict.items():
            if key not in ['foundBy','source','creation_date','modification_date']:
                if value is not None:
                    wikison+="|%s=%s\n" % (key,value)
        wikison+="}}\n"  
        return wikison

