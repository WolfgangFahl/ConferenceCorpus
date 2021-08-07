'''
Created on 2021-07-30

@author: wf
'''
from corpus.event import EventStorage
from corpus.eventcorpus import EventCorpus, EventDataSource

from datasources.confref import Confref
from datasources.crossref import Crossref
from datasources.dblp import Dblp
from datasources.wikidata import Wikidata
from datasources.openresearch import OR
from datasources.wikicfp import WikiCfp

from lodstorage.uml import UML
from wikibot.wikiuser import WikiUser
from wikifile.wikiFileManager import WikiFileManager

from datetime import datetime

import os
from os import path
import sys

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from lodstorage.query import QueryManager

class CorpusLookupConfigure:
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
            home = path.expanduser("~")
            wikiTextPath = f"{home}/.or/wikibackup/{wikiUser.wikiId}"
            wikiFileManager = WikiFileManager(wikiId, wikiTextPath, login=False, debug=debug)
     
            orDataSource=lookup.getDataSource(f'{lookupId}-backup')
            if orDataSource is not None:
                orDataSource.eventManager.wikiFileManager=wikiFileManager
                orDataSource.eventSeriesManager.wikiFileManager=wikiFileManager

            orDataSource=lookup.getDataSource(lookupId)
            if orDataSource is not None:
                orDataSource.eventManager.wikiUser=wikiUser
                orDataSource.eventSeriesManager.wikiUser=wikiUser
        
        pass

class CorpusLookup(object):
    '''
    search and lookup for different EventCorpora
    '''
    lookupIds=["confref","crossref","dblp","wikidata","wikicfp","or","or-backup","orclone","orclone-backup"]
    

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
        if "confref" in lookupIds:
            self.eventCorpus.addDataSource(Confref())
        if "crossref" in lookupIds:
            self.eventCorpus.addDataSource(Crossref())
        if "dblp" in lookupIds:
            self.eventCorpus.addDataSource(Dblp())
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


    def load(self,forceUpdate:bool=False):
        '''
        load the event corpora
        Args:
            forceUpdate(bool): True if the data should be fetched from the source instead of the cache
        '''
        if self.configure:
            self.configure(self)
        self.eventCorpus.loadAll(forceUpdate=forceUpdate)
        EventStorage.createViews()

    def getQueryManager(self):
        '''
        get the query manager
        '''
        cachedir=EventStorage.getStorageConfig().getCachePath()
        for path in cachedir,os.path.dirname(__file__)+"/../resources":
            qYamlFile=f"{path}/queries.yaml"
            if os.path.isfile(qYamlFile):
                qm=QueryManager(lang='sql',debug=self.debug,path=path)
                return qm
        return None

    def getLod4Query(self,query:str):
        '''
        Args:
            query: the query to run
        Return:
            list: the list of dicts for the query
        '''
        sqlDB=EventStorage.getSqlDB()
        listOfDicts=sqlDB.query(query)
        return listOfDicts

    def performQuery(self,query:str):
        '''
        Args:
            query: the query to run
        '''


    def asPlantUml(self,baseEntity='Event'):
        '''
        return me as a plantUml Diagram markup
        '''
        storageTableList=EventStorage.getTableList()
        schemaManager=None
        uml=UML()
        now=datetime.now()
        nowYMD=now.strftime("%Y-%m-%d")

        tableList=[]
        for table in storageTableList:
            tableName=table['name']
            prefix=f"{baseEntity.lower()}_"
            if tableName.startswith(prefix):
                if 'instances' in table:
                    instanceNote=""
                    dataSource=self.getDataSource4TableName(tableName)
                    if dataSource is not None:
                        sourceConfig=dataSource.sourceConfig
                        instanceNote=f"[[{sourceConfig.url} {sourceConfig.title}]]"
                    instanceCount=table['instances']
                    instanceNote=f"{instanceNote}\n{instanceCount} instances "
                    table['notes']=instanceNote
                tableList.append(table)
        title=f"""ConfIDent  {baseEntity}
{nowYMD}
[[https://projects.tib.eu/en/confident/ © 2019-2021 ConfIDent project]]
see also [[http://ptp.bitplan.com/settings Proceedings Title Parser]]
"""
        plantUml=uml.mergeSchema(schemaManager,tableList,title=title,packageName='DataSources',generalizeTo=baseEntity)
        return plantUml
        
        
__version__ = "0.0.17"
__date__ = '2020-06-22'
__updated__ = '2021-08-07'

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
  Copyright 2020-2021 Wolfgang Fahl. All rights reserved.

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
