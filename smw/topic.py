'''
Created on 2021-07-21

@author: wf
'''
from lodstorage.entity import EntityManager
from lodstorage.jsonable import JSONAble, JSONAbleList
from collections import OrderedDict
from lodstorage.lod import LOD
from wikibot.wikiuser import WikiUser
from wikibot.wikiclient import WikiClient
from wikibot.wikipush import WikiPush
from wikifile.wikiFileManager import WikiFileManager
from wikifile.wikiFile import WikiFile
from pathlib import Path

import os
import time


class SMWEntity(JSONAble):
    '''
    an Entity stored in Semantic MediaWiki in WikiSon notation
    '''

    def __init__(self, wikiFile=None):
        '''
        Constructor
        '''
        super().__init__()
        self.wikiFile = wikiFile

    @classmethod
    def fromWikiSonToLod(cls, record: dict, lookup: dict) -> dict:
        '''
        convert the given record from wikiSon to list of dict with the given lookup map

        Args:
            cls: the class this is called for
            record(dict): the original record in WikiSon format
            lookup(dict): the mapping of keys/names for the name/value pairs
        Return:
            dict: a dict which replaces name,value pairs with lookup[name],value pairs
        '''
        result = None
        if record:
            result = {}
            for propertyKey in lookup:
                templateKey = lookup[propertyKey].get('templateParam')
                if templateKey in record:
                    newKey = lookup[propertyKey].get('name')
                    if newKey is not None:
                        result[newKey] = record[templateKey]
                        # del record[key]
        return result


class SMWEntityList(object):
    '''
    Semantic MediaWiki backed entity list
    '''

    def __init__(self, entityManager:EntityManager):
        self.profile = False
        self.debug = False
        self.wikiClient = None
        self.wikiPush = None
        self.wikiFileManager = None
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
            for origEntity in self.getList():
                if origEntity.pageTitle == entity.pageTitle:
                    origAttributes = [*origEntity.__dict__]
                    difference = set(attributes) - set(origAttributes)
                    for attr in difference:
                        setattr(origEntity, attr, getattr(entity, attr))
                    return
            self.getList().append(entity)
        else:
            raise Exception('identifier not found in entity given')

    def getAskQuery(self, askExtra="", propertyLookupList=None):
        '''
        get the query that will ask for all my events

        Args:
           askExtra(str): any additional SMW ask query constraints
           propertyLookupList:  a list of dicts for propertyLookup

        Return:
            str: the SMW ask query
        '''
        entityName = self.getEntityName()
        selector = "IsA::%s" % entityName
        ask = """{{#ask:[[%s]]%s
|mainlabel=pageTitle
|?Creation date=creationDate
|?Modification date=modificationDate
|?Last editor is=lastEditor
""" % (selector, askExtra)
        if propertyLookupList is None:
            propertyLookupList = self.propertyLookupList
        for propertyLookup in propertyLookupList:
            propName = propertyLookup['prop']
            name = propertyLookup['name']
            ask += "|?%s=%s\n" % (propName, name)
        ask += "}}"
        return ask

    def fromWiki(self, wikiuser: WikiUser, askExtra="", profile=False):
        '''
        read me from a wiki using the given WikiUser configuration
        '''
        if self.wikiClient is None:
            self.wikiClient = WikiClient.ofWikiUser(wikiuser)
            self.wikiPush = WikiPush(fromWikiId=wikiuser.wikiId)
        askQuery = self.getAskQuery(askExtra)
        if self.debug:
            print(askQuery)
        startTime = time.time()
        entityName = self.getEntityName()
        records = self.wikiPush.formatQueryResult(askQuery, self.wikiClient, entityName=entityName)
        elapsed = time.time() - startTime
        if profile:
            print("query of %d %s records took %5.1f s" % (len(records), entityName, elapsed))
        self.fromLoD(records)
        return records

    def fromWikiFileManager(self, wikiFileManager):
        """
        initialize me from the given WikiFileManager
        """
        self.wikiFileManager = wikiFileManager
        wikiFileDict = wikiFileManager.getAllWikiFiles()
        self.fromWikiFiles(wikiFileDict.values())
        return self

    def fromWikiFiles(self, wikiFileList: list):
        '''
        initialize me from the given list of wiki files
        '''
        templateName = self.clazz.templateName
        wikiSonLod = WikiFileManager.convertWikiFilesToLOD(wikiFileList, templateName)
        lod = self.normalizeLodFromWikiSonToLod(wikiSonLod)
        self.fromLoD(lod)

    @classmethod
    def getPropertyLookup(cls) -> dict:
        '''
        get my PropertyLookupList as a map

        Returns:
            dict: my mapping from wiki property names to LoD attribute Names or None if no mapping is defined
        '''
        lookup = None
        if 'propertyLookupList' in cls.__dict__:
            propertyLookupList = cls.__dict__['propertyLookupList']
            lookup, _duplicates = LOD.getLookup(propertyLookupList, 'prop')
        return lookup

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

    @classmethod
    def normalizeLodFromWikiSonToLod(cls, wikiSonRecords: list) -> list:
        '''
        normalize the given LOD to the properties in the propertyLookupList

        Args:
            wikiSonRecords(list): the list of dicts to normalize/convert

        Return:
            list: a list of dict to retrieve entities from
        '''
        lookup = cls.getPropertyLookup()
        lod = []
        if lookup is not None:
            # convert all my records (in place)
            for record in wikiSonRecords:
                if not isinstance(record, dict):
                    continue
                normalizedDict = SMWEntity.fromWikiSonToLod(record, lookup)
                # make sure the pageTitle survives (it is not in the property mapping ...)
                if "pageTitle" in record:
                    normalizedDict["pageTitle"] = record["pageTitle"]
                lod.append(normalizedDict)
        return lod
