'''
Created on 2021-07-21

@author: wf
'''
import datetime
from typing import Callable
from lodstorage.entity import EntityManager
from lodstorage.jsonable import JSONAble
from wikibot.wikiuser import WikiUser
from wikibot.wikiclient import WikiClient
from wikibot.wikipush import WikiPush
from wikifile.wikiFileManager import WikiFileManager
from wikifile.wikiFile import WikiFile
from pathlib import Path

import time


class SMWEntity(object):
    '''
    an Entity stored in Semantic MediaWiki in WikiSon notation
    '''

    def __init__(self, entity:JSONAble, wikiFile:WikiFile=None):
        '''
        Constructor
        '''
        self.entity=entity
        self._wikiFile = wikiFile
        self._wikiFileManager = wikiFile.wikiFileManager if wikiFile else None

    @property
    def wikiFile(self):
        if self._wikiFile:
            return self._wikiFile
        else:
            pageTitle = getattr(self.entity, "pageTitle")
            wikiMarkup=getattr(self.entity, "wikiMarkup") if hasattr(self.entity, "wikiMarkup") else ""
            self._wikiFile=WikiFile(pageTitle, wikiFileManager=self.wikiFileManager, wikiText=wikiMarkup)
            return self._wikiFile

    @wikiFile.setter
    def wikiFile(self, wikiFile:WikiFile):
        '''Sets the wikiFile and overwrites the wikiMarkup of the entity'''
        self._wikiFile=wikiFile
        if hasattr(self.entity, "wikiMarkup"):
            setattr(self.entity,"wikiMarkup", wikiFile.wikiText)

    @property
    def wikiFileManager(self):
        return self._wikiFileManager

    @wikiFileManager.setter
    def wikiFileManager(self, wikiFileManager:WikiFileManager):
        self._wikiFileManager=wikiFileManager

    @staticmethod
    def updateDictKeys( record: dict, lookup: dict, reverseLookup:bool=False) -> dict:
        '''
        Updates the keys of the given record based on the given lookup dict.
        The key of the given lookup dict identifies the old key and the value the new key

        Args:
            record(dict): the record to be updated
            lookup(dict): the mapping of keys/names for the new key names
            reverseLookup(bool): If true the lookup is reversed
        Return:
            dict: given record with updated keys
        '''
        reverseDict = lambda d: {value:key for key, value in d.items()}
        result = None
        if record:
            result = {}
            if reverseLookup:
                lookup=reverseDict(lookup)
            for oldKey, newKey in lookup.items():
                if oldKey in record:
                    result[newKey] = record[oldKey]
        return result

    def updateWikiText(self, overwrite:bool=False):
        """Updates the WikiSon notation in the WikiText/WikiFile with the records of this entity"""
        wikiSonRecord = self.entity.__dict__.copy()
        lookup = self.entity.getTemplateParamLookup()
        if lookup:
            wikiSonRecord = self.updateDictKeys(wikiSonRecord, lookup, reverseLookup=True)
        # handle datetime to date (if only date do not add 00:00:00 as default time)
        for key, value in wikiSonRecord.items():
            if isinstance(value, datetime.datetime):
                if value.hour==0 and value.minute==0:
                    wikiSonRecord[key]=value.date()
        self.wikiFile.updateTemplate(self.entity.templateName, wikiSonRecord, prettify=True, overwrite=overwrite)

    def saveToWikiText(self, overwrite:bool=False):
        '''
        Saves the entity to a wikiText file. The wikiSon in the files is updated with the values of the entity
  
        Args:
            overwrite(bool): If True existing files might be overwritten
        '''
        self.updateWikiText(overwrite=overwrite)
        self.wikiFile.save_to_file(overwrite=overwrite)

    def pushToWiki(self, msg:str=None, overwrite:bool=False, wikiFileManager:WikiFileManager=None):
        """
        Pushes the wikiMarkup of this entity to the target wiki of the assigned wikiFileManager

        Args:
            msg(str): message to show on as comment on the pushed changes
            overwrite(bool): If True existing files might be overwritten
            wikiFileManager(WikiFileManager): Overwrites the wikiFileManager of this object if not None
        """
        if wikiFileManager:
            self.wikiFileManager=wikiFileManager
            if self._wikiFile:
                self.wikiFile.wikiFileManager=self.wikiFileManager
        self.updateWikiText(overwrite=overwrite)
        self.wikiFile.pushToWiki(msg=msg)



class SMWEntityList(object):
    '''
    Semantic MediaWiki backed entity list
    '''

    def __init__(self, entityManager:EntityManager, wikiFileManager:WikiFileManager=None):
        '''
        constructor
        '''
        self.entityManager=entityManager
        self.profile = False
        self.debug = False
        self.wikiClient = None
        self.wikiPush = None
        self.wikiFileManager = wikiFileManager
        self.askExtra = ""

    @classmethod
    def getDefaultCachePath(cls):
        '''
        get the defaultPath to my cache
        '''
        home = str(Path.home())
        cachedir = f"{home}/.smw"
        return cachedir

    def updateEntity(self, entity, identifier='pageTitle'):
        '''
        Add/Update the given entity in the entityList
        '''
        if hasattr(entity, identifier):
            attributes = [*entity.__dict__]
            for origEntity in self.entityManager.getList():
                if origEntity.pageTitle == entity.pageTitle:
                    origAttributes = [*origEntity.__dict__]
                    difference = set(attributes) - set(origAttributes)
                    for attr in difference:
                        setattr(origEntity, attr, getattr(entity, attr))
                    return
            self.entityManager.getList().append(entity)
        else:
            raise Exception('identifier not found in entity given')

    def getAskQuery(self, askExtra:str="", propertyLookupList=None):
        '''
        get the query that will ask for all my events

        Args:
           askExtra(str): any additional SMW ask query constraints
           propertyLookupList:  a list of dicts for propertyLookup

        Return:
            str: the SMW ask query
        '''
        entityName = self.entityManager.entityName
        selector = "IsA::%s" % entityName
        ask = f"""{{{{#ask:[[{selector}]]{askExtra}
|mainlabel=pageTitle
|?Creation date=creationDate
|?Modification date=modificationDate
|?Last editor is=lastEditor
"""
        if propertyLookupList is None:
            if self.entityManager is not None and hasattr(self.entityManager.clazz, 'propertyLookupList'):
                propertyLookupList = getattr(self.entityManager.clazz, 'propertyLookupList')
        for propertyLookup in propertyLookupList:
            propName = propertyLookup['prop']
            name = propertyLookup['name']
            ask += "|?%s=%s\n" % (propName, name)
        ask += "}}"
        return ask

    def fromWiki(self, wikiuser:WikiUser, askExtra="", profile=False):
        '''
        read me from a wiki using the given WikiUser configuration
        '''
        records=self.getLoDfromWiki(wikiuser,askExtra,profile)
        self.entityManager.fromLoD(records)
        return records

    def getLoDfromWiki(self, wikiuser:WikiUser, askExtra="", profile=False, limit:int=None):
        '''
        get the List of Dicts for the given wikiUser
        
        Args:
            wikiuser(WikiUser): the wikiuser to access the target wiki with
            askExtra(str): any addition to the default ask query
            profile(bool): if True show the timing for the operation
            limit(int): limit number of queried records
        '''
        if self.wikiClient is None:
            self.wikiClient = WikiClient.ofWikiUser(wikiuser)
            self.wikiPush = WikiPush(fromWikiId=wikiuser.wikiId)
        askQuery = self.getAskQuery(askExtra)
        if self.debug:
            print(askQuery)
        startTime = time.time()
        entityName = self.entityManager.entityName
        records = self.wikiPush.formatQueryResult(askQuery, self.wikiClient, entityName=entityName, limit=limit)
        elapsed = time.time() - startTime
        if profile:
            print("query of %d %s records took %5.1f s" % (len(records), entityName, elapsed))
        return records

    def getLoDfromWikiFileManager(self, wikiFileManager:WikiFileManager, limit:int=None):
        '''

        Args:
            wikiFileManager(WikiFileManager):
            limit(int): limits the number of loaded records
        Return:
            list of dicts
        '''
        if not self.wikiFileManager and wikiFileManager:
            self.wikiFileManager = wikiFileManager
        wikiFileDict = self.wikiFileManager.getAllWikiFiles()
        lod=self.getLoDfromWikiFiles(list(wikiFileDict.values()), limit=limit)
        for record in lod:
            pageTitle=record.get("pageTitle")
            wikiFile=wikiFileDict.get(pageTitle)
            if isinstance(wikiFile, WikiFile):
                record["wikiMarkup"]=wikiFile.wikiText
        return lod

    def getLoDfromWikiFiles(self, wikiFileList: list, limit:int=None):
        '''
        Convert given wikiFiles to LoD

        Args:
            wikiFileList(list):
            limit(int): limits the number of loaded records

        Return:
            list of dicts
        '''
        templateName = self.entityManager.clazz.templateName
        wikiSonLod = WikiFileManager.convertWikiFilesToLOD(wikiFileList, templateName, limit=limit)
        lod = self.normalizeLodFromWikiSonToLod(wikiSonLod)
        return lod

    def fromWikiFileManager(self, wikiFileManager):
        """
        initialize me from the given WikiFileManager
        """
        lod=self.getLoDfromWikiFileManager(wikiFileManager)
        self.entityManager.fromLoD(lod)

    def fromWikiFiles(self, wikiFileList: list):
        '''
        initialize me from the given list of wiki files
        '''
        lod=self.getLoDfromWikiFiles(wikiFileList)
        self.entityManager.fromLoD(lod)

    def fromSampleWikiSonLod(self, entityClass):
        '''
        get a list of dicts derived form the wikiSonSamples

        Returns:
            list: a list of dicts for my sampleWikiText in WikiSon notation
        '''
        wikiFileList = []
        for sampleWikiText in entityClass.getSampleWikiTextList():
            pageTitle = None
            wikiFile = WikiFile(name=pageTitle, wikiText=sampleWikiText)
            wikiFileList.append(wikiFile)
        self.fromWikiFiles(wikiFileList)

    def normalizeLodFromWikiSonToLod(self, wikiSonRecords: list) -> list:
        '''
        normalize the given LOD to the properties in the propertyLookupList

        Args:
            wikiSonRecords(list): the list of dicts to normalize/convert

        Return:
            list: a list of dict to retrieve entities from
        '''
        lod = []
        lookup=None
        if callable(getattr(self.entityManager.clazz, "getPropertyLookup", None)):
            lookup=self.entityManager.clazz.getTemplateParamLookup()
        if lookup:
            for record in wikiSonRecords:
                if not isinstance(record, dict):
                    continue
                normalizedDict = SMWEntity.updateDictKeys(record, lookup)
                # make sure the pageTitle survives (it is not in the property mapping ...)
                if "pageTitle" in record:
                    normalizedDict["pageTitle"] = record["pageTitle"]
                lod.append(normalizedDict)
        return lod

    def updateEntityToWiki(self, entity, overwrite:bool = True, targetWiki=None, uploadToWikiCallback:Callable = None):
        if hasattr(entity, 'pageTitle'):
            self.interlinkEntitiesWithWikiMarkupFile()
            entity.smwHandler.saveToWikiText(overwrite=overwrite)
            wikiFile = self.wikiFileManager.getWikiFile(entity.pageTitle)
            if uploadToWikiCallback is not None:
                uploadToWikiCallback(wikiFile,targetWiki)

    def interlinkEntitiesWithWikiMarkupFile(self, useCacheIfPresent:bool=False):
        '''
        Assigns the correspondingWikiFile to the SMWEntity
        '''
        for entity in self.entityManager.getList():
            if hasattr(entity, "pageTitle"):
                pageTitle=entity.pageTitle
                if hasattr(entity, "smwHandler") and isinstance(getattr(entity, "smwHandler"), SMWEntity):
                    smwHandler=entity.smwHandler
                    if useCacheIfPresent and hasattr(entity, "wikiMarkup"):
                        smwHandler.wikiFileManager=self.wikiFileManager
                        smwHandler._wikiFile=None
                    else:
                        wikiFile=self.wikiFileManager.getWikiFile(entity.pageTitle)
                        smwHandler.wikiFile=wikiFile