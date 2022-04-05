'''
Created on 2021-07-30

@author: wf
'''
from corpus.event import EventStorage
from corpus.eventcorpus import EventCorpus, EventDataSource
from corpus.datasources.acm import ACM
from corpus.datasources.confref import Confref
from corpus.datasources.crossref import Crossref
from corpus.datasources.dblp import Dblp
from corpus.datasources.gnd import GND
from corpus.datasources.tibkat import Tibkat
from corpus.datasources.wikidata import Wikidata
from corpus.datasources.openresearch import OR
from corpus.datasources.wikicfp import WikiCfp

from lodstorage.uml import UML
from lodstorage.lod import LOD
from wikibot.wikiuser import WikiUser
from wikifile.wikiFileManager import WikiFileManager

from datetime import datetime

import os
import re
from os import path
import sqlite3
import sys
import getpass

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter


class CorpusLookupConfigure:
    '''
    Configuration of the Corpus Lookup
    '''
    @staticmethod
    def getWikiTextPath(wikiId:str):
        ''' 
        get the WikiText (Backup) path for the given wikiId
        
        Args:
            wikiId(str): the wikiId (e.g. "or", "orclone"
            
        Return:
            the path to the backup files as created by the wikibackup script
        '''
        home = path.expanduser("~")
        wikiTextPath = f"{home}/.or/wikibackup/{wikiId}"
        return wikiTextPath
            
    @staticmethod
    def configureCorpusLookup(lookup,debug=False):
        '''
        callback to configure the corpus lookup
        '''
        print("configureCorpusLookup callback called")
        # TODO make wikiIds configurable for testing e.g. with pyMediaWikiDocker
        for lookupId in ["or","orclone"]:
            wikiId=lookupId
            wikiUser=WikiUser.ofWikiId(wikiId, lenient=True)
            wikiTextPath = CorpusLookupConfigure.getWikiTextPath(wikiUser.wikiId)
            wikiFileManager = WikiFileManager(wikiId, wikiTextPath, login=False, debug=debug)
     
            orDataSource=lookup.getDataSource(f'{lookupId}-backup')
            if orDataSource is not None:
                orDataSource.eventManager.smwHandler.wikiFileManager=wikiFileManager
                orDataSource.eventSeriesManager.smwHandler.wikiFileManager=wikiFileManager

            orDataSource=lookup.getDataSource(lookupId)
            if orDataSource is not None:
                orDataSource.eventManager.wikiUser=wikiUser
                orDataSource.eventSeriesManager.wikiUser=wikiUser
        
        pass

class CorpusLookup(object):
    '''
    search and lookup for different EventCorpora
    '''
    lookupIds=["confref","crossref","dblp","gnd","wikidata","wikicfp","or","or-backup","orclone","orclone-backup"]
    

    def __init__(self,lookupIds:list=None,
                 configure:callable=None,debug=False):
        '''
        Constructor
        
        Args:
            lookupIds(list): the list of lookupIds to addDataSources for
            configure(callable): Callback to configure the corpus lookup
        '''
        self.debug=debug
        self.configure=configure
        self.eventCorpus=EventCorpus()
        if lookupIds is None:
            lookupIds=CorpusLookup.lookupIds
            user=getpass.getuser()
            # TODO enable generally
            if user=="wf":
                lookupIds.append("tibkat") 
        if "acm" in lookupIds:
            self.eventCorpus.addDataSource(ACM())
        if "confref" in lookupIds:
            self.eventCorpus.addDataSource(Confref())
        if "crossref" in lookupIds:
            self.eventCorpus.addDataSource(Crossref())
        if "dblp" in lookupIds:
            self.eventCorpus.addDataSource(Dblp())
        if "gnd" in lookupIds:
            self.eventCorpus.addDataSource(GND())
        if "tibkat" in lookupIds:
            self.eventCorpus.addDataSource(Tibkat())
        if "wikidata" in lookupIds: 
            self.eventCorpus.addDataSource(Wikidata())
        if "wikicfp" in lookupIds:    
            self.eventCorpus.addDataSource(WikiCfp())
        if "or" in lookupIds:    
            self.eventCorpus.addDataSource(OR(wikiId="or",via="api"))
        if "or-backup" in lookupIds:    
            self.eventCorpus.addDataSource(OR(wikiId="or",via="backup"))
        if "orclone" in lookupIds:    
            self.eventCorpus.addDataSource(OR(wikiId="orclone",via="api"))
        if "orclone-backup" in lookupIds:    
            self.eventCorpus.addDataSource(OR(wikiId="orclone",via="backup"))
        
    def getDataSource(self,lookupId:str)->EventDataSource:
        '''
        get the data source by the given lookupId
        
        Args:
            lookupId(str): the lookupId of the data source to get
            
        Return:
            EventDataSource: the data source

        '''
        eventDataSource=None
        if lookupId in self.eventCorpus.eventDataSources:
            eventDataSource=self.eventCorpus.eventDataSources[lookupId]
        return eventDataSource

    def getDataSource4TableName(self,tableName:str)->EventDataSource:
        '''
        get the data source by the given tableName

        Args:
            tableName(str): a tableName of the data source to get

        Return:
            EventDataSource: the data source

        '''
        for eventDataSource in self.eventCorpus.eventDataSources.values():
            if eventDataSource.eventManager.tableName==tableName:
                return eventDataSource
            if eventDataSource.eventSeriesManager.tableName==tableName:
                return eventDataSource
        return None


    def load(self,forceUpdate:bool=False,showProgress:bool=False,withCreateViews=True):
        '''
        load the event corpora
        
        Args:
            forceUpdate(bool): if True the data should be fetched from the source instead of the cache
            showProgress(bool): if True the progress of the loading should be shown
        '''
        if self.configure:
            self.configure(self)
        self.eventCorpus.loadAll(forceUpdate=forceUpdate,showProgress=showProgress)
        if withCreateViews:
            EventStorage.createViews(exclude=EventStorage.viewTableExcludes)
    
    def getDataSourceInfos(self,withInstanceCount:bool=True):
        '''
        get the dataSource Infos
        '''
        infos=[]
        for dataSourceName,dataSource in self.eventCorpus.eventDataSources.items():
            info={
                "source":dataSourceName,
                "title": dataSource.sourceConfig.title,
                "url":dataSource.sourceConfig.url,
                "lookupId": dataSource.sourceConfig.lookupId,
                "tableSuffix": dataSource.sourceConfig.tableSuffix
            }
            if withInstanceCount:
                em=dataSource.eventManager
                esm=dataSource.eventSeriesManager
                for title,manager in [("event",em),("series",esm)]:
                    query=f"SELECT count(*) as count from {manager.tableName}"
                    lod=self.getLod4Query(query)
                    record=lod[0]
                    info[title]=record["count"]
            infos.append(info)
        return infos
            
    def getLod4Query(self,query:str,params=None):
        '''
        Args:
            query: the query to run
            params(tuple): the query params, if any
        Return:
            list: the list of dicts for the query
        '''
        sqlDB=EventStorage.getSqlDB()
        listOfDicts=sqlDB.query(query,params)
        return listOfDicts
    
    def getMultiQueryVariable(self,multiquery:str,lenient:bool=False):
        '''
        get the variable being used in a multiquery
        
        Args:
            multiquery(str): the multiquery containing a {variable}
            lenient(bool): if True allow to return a None value otherwise raise an Exception if no variable was found
            
        Returns:
            str: variable
            
        Raises:
            Exception: if lenient is False and no variable was found
            
        '''
        var=None
        regEx=r"\{(.*)\}"
        varMatch=re.search(regEx, multiquery)
        # which variable to we want to replace?
        if varMatch:
            var=varMatch.group(1)
        else:
            if not lenient:
                raise Exception("need a variable for the tableName to be queried in {viewName} notation")   
        return var
    
    def getDictOfLod4MultiQuery(self,multiquery:str,idQuery:str=None,omitFailed:bool=True)->dict:
        '''
        Args:
            multiquery(str): the multi query containing a variable
            idQuery(str): optional query to get lists of ids for selection
            omitFaild(bool): if True omit failed queries if False raise Exception on failure
            
        Return:
            dict: the dict of list of dicts for the queries derived
            from the multi query
            
        Raises:
            Exception: if omitFailed is False and an error occured for a query
        '''
        dataSourceInfos=self.getDataSourceInfos(withInstanceCount=False)
        dataSourcesByTableSuffix,_dup=LOD.getLookup(dataSourceInfos, "tableSuffix")
        viewName=self.getMultiQueryVariable(multiquery)
        variable="{%s}" % viewName
        dictOfLod={}
        # if an idquery is given create a dictionary of ids pers source
        if idQuery:
            idLod=self.getLod4Query(idQuery)
            idDict={}
            idColumn=f"{viewName}Id"
            for idRecord in idLod:
                source=idRecord["source"]
                recordId=f"'{idRecord[idColumn]}'"
                if source in idDict:
                    idDict[source].append(recordId)
                else:
                    idDict[source]=[recordId]
        # get the tables to potentially query 
        tableList=EventStorage.getViewTableList(viewName, exclude=EventStorage.viewTableExcludes)
        # loop over all relevant tables
        for table in tableList:
            tableName=table["name"]
            # create the base query per table by replacing the viewname for the base table
            queryPrefix=multiquery.replace(variable,tableName)
            tableSuffix=tableName.replace(f"{viewName}_","")
            # do we have a data source for the table?
            if tableSuffix in dataSourcesByTableSuffix:
                # are we going to actually query?
                queryDataSource=True
                whereClause=""
                # get the dataSource
                dataSourceName=dataSourcesByTableSuffix[tableSuffix]["lookupId"]
                # shall we select only certain ids?
                if idQuery:
                    # do we have an idList?
                    if dataSourceName in idDict: 
                        idList=",".join(idDict[dataSourceName])
                        whereClause=f" WHERE {idColumn} in ({idList})"
                    else:
                        # no idList - do not query at all
                        queryDataSource=False
                # if we want to query
                if queryDataSource:
                    # query the table
                    query=f"{queryPrefix}{whereClause}"
                    try:
                        # get the list of dicts
                        lod=self.getLod4Query(query)
                        # put the result into the dict for the given datasource
                        dictOfLod[dataSourceName]=lod
                    except sqlite3.OperationalError as ex:
                        if not omitFailed:
                            raise ex
        return dictOfLod


    def asPlantUml(self,baseEntity='Event',exclude=None):
        '''
        return me as a plantUml Diagram markup
        '''
        schemaManager=None
        uml=UML()
        now=datetime.now()
        nowYMD=now.strftime("%Y-%m-%d")
        viewName=f"{baseEntity.lower()}"
        tableList=EventStorage.getViewTableList(viewName, exclude=exclude)
        for table in tableList:
            tableName=table['name']
            if 'instances' in table:
                instanceNote=""
                dataSource=self.getDataSource4TableName(tableName)
                if dataSource is not None:
                    sourceConfig=dataSource.sourceConfig
                    instanceNote=f"[[{sourceConfig.url} {sourceConfig.title}]]"
                instanceCount=table['instances']
                instanceNote=f"{instanceNote}\n{instanceCount} instances "
                table['notes']=instanceNote
        title=f"""ConfIDent  {baseEntity}
{nowYMD}
[[https://projects.tib.eu/en/confident/ © 2019-2022 ConfIDent project]]
see also [[http://ptp.bitplan.com/settings Proceedings Title Parser]]
"""
        plantUml=uml.mergeSchema(schemaManager,tableList,title=title,packageName='DataSources',generalizeTo=baseEntity)
        return plantUml
        
        
__version__ = "0.0.27"
__date__ = '2020-06-22'
__updated__ = '2022-01-03'

DEBUG = 1

    
def main(argv=None): # IGNORE:C0111
    '''main program.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)    
        
    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = "Scientific Event Corpus and Lookup"
    user_name="Wolfgang Fahl"
    program_license = '''%s

  Created by %s on %s.
  Copyright 2020-2022 Wolfgang Fahl. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, user_name,str(__date__))

    try:
        # Setup argument parser
        datasourcesDefault=",".join(CorpusLookup.lookupIds)
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-d", "--debug", dest="debug", action="store_true", help="show debug info")
        parser.add_argument("-q", "--query",help="run the given query")
        parser.add_argument('-e', '--endpoint', default=Wikidata.endpoint, help="SPARQL endpoint to use for wikidata queries")
        parser.add_argument('-v', '--version', action='version', version=program_version_message)
        parser.add_argument("-u", "--uml", dest="uml", action="store_true", help="output plantuml diagram markup")
        parser.add_argument("-f", "--force",dest="forceUpdate",action="store_true",help="force Update - may take quite a time")
        parser.add_argument("--datasources",help=", delimited list of datasource lookup ids",default=datasourcesDefault)
        
        # Process arguments
        args = parser.parse_args()   
        Wikidata.endpoint=args.endpoint
        lookupIds=args.datasources.split(",")
        lookup=CorpusLookup(debug=args.debug,lookupIds=lookupIds,configure=CorpusLookupConfigure.configureCorpusLookup)
        lookup.load(forceUpdate=args.forceUpdate)
        if args.uml:
            for baseEntity in ["Event","EventSeries"]:
                plantUml=lookup.asPlantUml(baseEntity)
                print(plantUml)
        if args.query:
            lookup.query(args.query)

        
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 1
    except Exception as e:
        if DEBUG:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2         
        
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(main())
