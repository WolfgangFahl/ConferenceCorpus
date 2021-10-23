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
from lodstorage.storageconfig import StorageConfig
from corpus.quality.rating import RatingManager,Rating
from corpus.eventrating import EventRating,EventSeriesRating
from lodstorage.sparql import SPARQL

import re
class EventStorage:
    '''
    common storage aspects of the EventManager and EventSeriesManager
    '''
    profile=True
    withShowProgress=False
    
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
    def getSqlDB(cls):
        '''
        get the SQL Database
        '''
        config=EventStorage.getStorageConfig()
        sqlDB=SQLDB(config.cacheFile)
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
    def getCommonViewDDLs(cls,exclude=None):
        '''
        get the SQL DDL for a common view 
        
        Return:
            str: the SQL DDL CREATE VIEW command
        '''
        # TODO use generalize instead of fixed list
        commonMap={
            "event": "eventId,title,url,city,country,region,countryIso,regionIso,acronym,source,year",
            "eventseries": "source"
        }
        viewDDLs=[]
        for viewName in commonMap.keys():
            createViewDDL=f"""CREATE VIEW IF NOT EXISTS {viewName} AS\n"""
            delim=""
            common=commonMap[viewName]
            sqlDB=EventStorage.getSqlDB()
            tableList=sqlDB.getTableList()
            for table in tableList:
                tableName=table["name"]
                if tableName.startswith(f"{viewName}_"):
                    include=True
                    if exclude is not None:
                        include=tableName not in exclude
                    if include:
                        createViewDDL=f"{createViewDDL}{delim}  SELECT {common} FROM {tableName}"
                        delim="\nUNION\n" 
            viewDDLs.append(createViewDDL)
        return viewDDLs
        
    @classmethod
    def createViews(cls):
        ''' 
          create the general Event view
          
        Args:
            cacheFileName(string): the path to the database
        '''
        sqlDB=EventStorage.getSqlDB()
        viewDDLs=EventStorage.getCommonViewDDLs()
        for viewDDL in viewDDLs:
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
        dblpConferenceId=re.sub("^conf\/","",self.eventId)
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
        super().__init__(name, entityName, entityPluralName, listName, clazz, tableName, primaryKey, config, handleInvalidListTypes, filterInvalidListTypes, debug)
   
        
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

    def updateFromLod(self, lod:list, overwriteEvents:bool = True, updateEntitiesCallback:Callable =None):
        """
        Updates the entities from the given LoD. If a entity does not already exist a new one will be added.
        Args:
            lod: data to update the entities
            overwriteEvents: If False only missing values are added
            updateEntitiesCallback: Callback function that is called on an updated entity

        Returns:

        """
        originalEventsLookup = self.getLookup(attrName=self.primaryKey)[0]
        for eventRecord in lod:
            if self.primaryKey in eventRecord:
                eventRecordPrimaryKey = eventRecord.get(self.primaryKey)
                if eventRecordPrimaryKey in originalEventsLookup:
                    originalEvent = originalEventsLookup[eventRecordPrimaryKey]
                    if hasattr(originalEvent, self.primaryKey):
                        for key, value in eventRecord.items():
                            if hasattr(originalEvent, key):
                                setattr(originalEvent, key, value)
                        if updateEntitiesCallback is not None and callable(updateEntitiesCallback):
                            updateEntitiesCallback(originalEvent, overwrite=overwriteEvents)
                else:
                    self.fromLoD(lod=[eventRecord], append=True, debug=self.debug)
                    # new entity was addded → update lookup
                    originalEventsLookup = self.getLookup(attrName=self.primaryKey)[0]
                    originalEvent = originalEventsLookup[eventRecordPrimaryKey]
                    if updateEntitiesCallback is not None and callable(updateEntitiesCallback):
                        updateEntitiesCallback(originalEvent, overwrite=overwriteEvents)

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
        '''
        sparql=SPARQL(self.endpoint)
        query=self.getSparqlQuery()
        listOfDicts=sparql.queryAsListOfDicts(query)
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
        if seriesAcronym in self.seriesAcronymLookup:
            seriesEvents = self.seriesLookup[seriesAcronym]
            if self.debug:
                print(f"{seriesAcronym}:{len(seriesEvents):4d}")
        else:
            if self.debug:
                print(f"Event Series Acronym {seriesAcronym} lookup failed")
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

