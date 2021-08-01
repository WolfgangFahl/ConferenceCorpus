'''
Created on 2021-07-39

@author: wf
'''
from corpus.event import EventStorage
from corpus.eventcorpus import EventCorpus, EventDataSource

from datasources.dblp import DblpEventManager,DblpEventSeriesManager
from datasources.wikidata import Wikidata,WikidataEventManager,WikidataEventSeriesManager
from datasources.openresearch import OREventManager,OREventSeriesManager
from datasources.wikicfp import WikiCfpEventManager,WikiCfpEventSeriesManager

from lodstorage.uml import UML

from datetime import datetime

import os
import sys

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

class CorpusLookup(object):
    '''
    search and lookup for different EventCorpora
    '''

    def __init__(self,lookupIds=["dblp","wikidata","wikicfp","or","or-backup","orclone","orclone-backup"],
                 configure:callable=None,debug=False):
        '''
        Constructor
        
        Args:
            configure(callable): Callback to configure the corpus lookup
        '''
        self.debug=debug
        self.configure=configure
        self.eventCorpus=EventCorpus()
        if "dblp" in lookupIds:
            self.eventCorpus.addDataSource(DblpEventManager(),DblpEventSeriesManager(),lookupId="dblp",name="dblp",url='https://dblp.org/',title='dblp computer science bibliography',tablePrefix="dblp")
        if "wikidata" in lookupIds: 
            self.eventCorpus.addDataSource(WikidataEventManager(),WikidataEventSeriesManager(),lookupId="wikidata",name="Wikidata",url='https://www.wikidata.org/wiki/Wikidata:Main_Page',title='Wikidata',tablePrefix="wikidata")
        if "wikicfp" in lookupIds:    
            self.eventCorpus.addDataSource(WikiCfpEventManager(),WikiCfpEventSeriesManager(),lookupId="wikicfp",name="WikiCFP",url='http://www.wikicfp.com',title='WikiCFP',tablePrefix="wikicfp")
        if "or" in lookupIds:    
            self.eventCorpus.addDataSource(OREventManager(),OREventSeriesManager(),lookupId="or",name="OR_Triples",url='https://www.openresearch.org/wiki/Main_Page',title='OPENRESEARCH-api',tablePrefix="orapi")
        if "or-backup" in lookupIds:    
            self.eventCorpus.addDataSource(OREventManager(),OREventSeriesManager(),lookupId="or-backup",name="OR_Markup",url='https://www.openresearch.org/wiki/Main_Page',title='OPENRESEARCH-wiki',tablePrefix="orwiki")
        if "orclone" in lookupIds:    
            self.eventCorpus.addDataSource(OREventManager(),OREventSeriesManager(),lookupId="orclone",name="OR_Clone_Triples",url='https://confident.dbis.rwth-aachen.de/or/index.php?title=Main_Page',title='OPENRESEARCH-clone-api',tablePrefix="orcapi")
        if "orclone-backup" in lookupIds:    
            self.eventCorpus.addDataSource(OREventManager(),OREventSeriesManager(),lookupId="orclone-backup",name="OR_Clone_Markup",url='https://confident.dbis.rwth-aachen.de/or/index.php?title=Main_Page',title='OPENRESEARCH-clone-wiki',tablePrefix="orcwiki")
        
    def getDataSource(self,lookupId:str)->EventDataSource:
        '''
        get the given data source
        
        Args:
            lookupId(str): the lookupId of the data source to get
            
        Return:
            EventDataSource: the data source

        '''
        eventDataSource=None
        if lookupId in self.eventCorpus.eventDataSources:
            eventDataSource=self.eventCorpus.eventDataSources[lookupId]
        return eventDataSource
        
    def load(self):
        '''
        load the event corpora
        '''
        if self.configure:
            self.configure(self)
        self.eventCorpus.loadAll()
        
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
            if tableName.endswith(baseEntity):
                if 'instances' in table:
                    instanceNote=""
                    instanceCount=table['instances']
                    instanceNote=f"\n{instanceCount} instances "
                    table['notes']=instanceNote
                tableList.append(table)
        title=f"""ConfIDent  {baseEntity}
{nowYMD}
[[https://projects.tib.eu/en/confident/ © 2019-2021 ConfIDent project]]
see also [[http://ptp.bitplan.com/settings Proceedings Title Parser]]
"""
        plantUml=uml.mergeSchema(schemaManager,tableList,title=title,packageName='DataSources',generalizeTo=baseEntity)
        return plantUml
        
        
__version__ = "0.0.6"
__date__ = '2020-06-22'
__updated__ = '2021-08-01'    

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
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    user_name="Wolfgang Fahl"
    program_license = '''%s

  Created by %s on %s.
  Copyright 2020 Wolfgang Fahl. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, user_name,str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-d", "--debug", dest="debug", action="store_true", help="show debug info")
        parser.add_argument('-e', '--endpoint', default=Wikidata.endpoint, help="SPARQL endpoint to use for wikidata queries")     
        parser.add_argument('-v', '--version', action='version', version=program_version_message)
        parser.add_argument("-u", "--uml", dest="uml", action="store_true", help="output plantuml diagram markup")
        
        # Process arguments
        args = parser.parse_args()   
        Wikidata.endpoint=args.endpoint
        lookup=CorpusLookup(debug=args.debug)
        lookup.load()
        if args.uml:
            for baseEntity in ["Event","EventSeries"]:
                plantUml=lookup.asPlantUml(baseEntity)
            print(plantUml)
        
        
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