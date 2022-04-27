'''
Created on 2022-03-05

@author: wf
'''
import os
import sys
import traceback
from lodstorage.lod import LOD
from corpus.version import Version
from corpus.lookup import CorpusLookup, CorpusLookupConfigure
from corpus.locationfixer import LocationFixer
from corpus.datasources.dblpxml import DblpXml
from corpus.datasources.tibkat import Tibkat
from corpus.utils.download import Profiler
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from corpus.event import EventStorage
from ptp.eventrefparser import EventReferenceParser

class ConferenceCorpusUpdate():
    '''
    updater for the Conference Corpus database
    
    allows updating single or multiple datasources of the conferencecorpus
    e.g. via command line
    '''
    def __init__(self,lookupId:str, debug:bool=False):
        '''
        constructor
        
        Args:
            lookupId(str): the lookupId of the dataSource to be used
            debug(bool): If True show debug messages
        '''
        self.debug=debug
        self.lookupId=lookupId
        
    def getEventDataSource(self,forceUpdate:bool=False):
        '''
        get my event data source
        
        Args:    
            forceUpdate(bool): if True force updating the event data source
        
        Returns:
            EventDataSource: the event data source for my lookup id
        '''
        lookup=CorpusLookup(lookupIds=[self.lookupId], debug=self.debug)
        lookup.load(forceUpdate=forceUpdate,showProgress=True)
        eventDataSource=lookup.getDataSource(self.lookupId)
        return eventDataSource
        
    def updateDataSource(self,source:str,sampleId:str=None):
        '''
        update the given DataSource
        
        Args:
            source(str): the name of the datasource to update
            sampleId(str): the id of the sample record to display when done
        '''
        msg=f"update of conference corpus database from {source}"
        profiler=Profiler(msg)
        eventDataSource=self.getEventDataSource(forceUpdate=True)
        el=eventDataSource.eventManager.getList()
        esl=eventDataSource.eventSeriesManager.getList()
        msg=f"{eventDataSource.name}: {len(el)} events {len(esl)} eventseries"
        profiler.time(msg)
        eventsByAcronym,_dup=LOD.getLookup(el, "acronym")
        if sampleId is not None:
            if sampleId in eventsByAcronym:
                event=eventsByAcronym[sampleId]
                print (event.toJSON())
            else:
                print(f"sample event id {sampleId} not found")
                
    def addLookupAcronyms(self):
        '''
        add lookup acronyms
        '''
        msg=f"adding lookup acronyms for {self.lookupId}"
        profiler=Profiler(msg)
        eventDataSource=self.getEventDataSource(forceUpdate=False)
        el=eventDataSource.eventManager.getList()
        for event in el:
            event.getLookupAcronym()
        eventDataSource.eventManager.store()
        msg=f"{eventDataSource.name}: added lookupAcronym for {len(el)} events"
        profiler.time(msg)
        
    
class TibkatUpdater(ConferenceCorpusUpdate):
    '''
    update for Tibkat data from FTX XML dump
    '''
    
    def __init__(self):
        '''
        constructor
        '''
        super().__init__("tibkat")
        
    def update(self,args):
        '''
        update
        
        Args:
            args: command line arguments
        '''
        if args.updateConferenceCorpus or args.updateAll:
            Tibkat.limitFiles=args.limitFiles
            Tibkat.ftxroot=args.ftxroot
            Tibkat.wantedbks=args.wantedBks
            if Tibkat.wantedbks==["all"]:
                Tibkat.wantedbks=[]
            super().updateDataSource(source=f"TIBKAT FTX dump \nftxroot:{args.ftxroot}\nlimitFiles:{args.limitFiles}\nBasisklassifikationen: {args.wantedBks}",sampleId=args.sample)
        

class DblpUpdater(ConferenceCorpusUpdate):
    '''
    updater for Dblp data from XML dump
    '''
    
    def __init__(self):
        '''
        constructor
        '''
        super().__init__("dblp")
            
    def update(self,args):
        '''
        update
        
        Args:
            args: command line arguments
        '''
        debug=args.debug
        dblpXml=DblpXml(debug=debug)
        reload=args.updateXml or args.updateAll
        xmlfile=dblpXml.getXmlFile(reload=reload)
        sizeMB=dblpXml.getSize()/1024/1024
        print(f"dblp xml dump file is  {xmlfile} with size {sizeMB:5.1f} MB" )
        if args.updateXml or args.updateAll:
            showProgress=True
            recreate=True
            limit=10000000
            sample=5
            _sqlDB=dblpXml.getSqlDB(limit, sample=sample, debug=debug,recreate=recreate,postProcess=dblpXml.postProcess,showProgress=showProgress)
        if args.updateConferenceCorpus or args.updateAll:
            super().updateDataSource("dblp xml dump","ISWC 2008") 

def main(argv=None): # IGNORE:C0111
    '''main program.'''

    if argv is None:
        argv=sys.argv[1:]
        
    program_name = os.path.basename(__file__)
    program_version = "v%s" % Version.version
    program_build_date = str(Version.updated)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = "Conference Corpus update from command line"
    user_name="Wolfgang Fahl/Tim Holzheim"
    program_license = '''%s

  Created by %s on %s.
  Copyright 2022 contributors. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc,user_name, str(Version.date))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-d",   "--debug", dest="debug", action="store_true", help="set debug [default: %(default)s]")
        parser.add_argument("--createViews",action="store_true",help="create the common view for all datasources")
        parser.add_argument("--createLookup",action="store_true",help="create lookup yaml files for city,country and region for the given table prefixes")
        parser.add_argument("--lookupTables",nargs="+",default=["dblp","wikidata","crossref","confref"],help="tables to use for lookup Creation\n[default: %(default)s]")
        parser.add_argument("-dblp","--dblp", dest="dblp",   action="store_true", help="update dblp")
        parser.add_argument("--tibkat", action="store_true",help="update tibkat from ftx")
        parser.add_argument("--fixlocations",nargs="+",help="fix the locations for the given lookup Ids")
        parser.add_argument("--perCentLimit",type=float,default=60.0,help="limit the percentage of Locations to be covered [default: %(default)s]")
        parser.add_argument("--addLookupAcronym",nargs="+",help="add lookupAcronyms for the given lookup Ids")
        parser.add_argument("--updateSource",nargs="+",help="update the sources for the given lookup Ids")
        parser.add_argument("--limitFiles",type=int,default=10000,help="limit the number of file to be parsed [default: %(default)s]")
        parser.add_argument("--ftxroot",default="/Volumes/seel/tibkat-ftx/tib-intern-ftx_0/tib-2021-12-20",help="path to root directory of ftx xml files [default: %(default)s]")
        parser.add_argument("--sample",default="ISWC 2008",help="sample event ID [default: %(default)s]")
        parser.add_argument("--wantedBks",nargs="+",default=["54"],help="wanted Basisklassifikationen [default: %(default)s] use 'all' for no filter")
        parser.add_argument("-uxml","--updateXml", dest="updateXml",   action="store_true", help="update the dblp xml file and eventcorpus database")
        parser.add_argument("-ucc","--updateConferenceCorpus", dest="updateConferenceCorpus",   action="store_true", help="update the dblp xml file and eventcorpus database")
        parser.add_argument("-uall","--updateAll", dest="updateAll",   action="store_true", help="update the dblp xml file and eventcorpus database")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        
        args = parser.parse_args(argv)
        if args.debug:
            DEBUG = True
            print("Starting in debug mode")
        if args.dblp:
            dblpUpdater=DblpUpdater()
            dblpUpdater.update(args)
        if args.tibkat:
            tibkatUpdater=TibkatUpdater()
            tibkatUpdater.update(args)
        if args.fixlocations:
            locationFixer=LocationFixer()
            locationFixer.fixLocations4LookupIds(args.fixlocations,args.perCentLimit)
        if args.updateSource:
            for lookupId in args.updateSource:
                updater=ConferenceCorpusUpdate(lookupId, debug=args.debug)
                updater.updateDataSource(f"{lookupId} cache", args.sample)
        if args.addLookupAcronym:
            for lookupId in args.addLookupAcronym:
                updater=ConferenceCorpusUpdate(lookupId)
                updater.addLookupAcronyms()
        if args.createLookup:
            tables=args.lookupTables
            eParser=EventReferenceParser()
            yamlPath="/tmp"
            for column,columnPlural in [("country","countries"),("city","cities"),("region","regions")]:
                lookup=EventStorage.createLookup(column,tables)
                eParser.lookupToYaml(lookup, columnPlural, tables, yamlPath,show=True)
            
        if args.createViews:
            profiler=Profiler("Creating common views")
            EventStorage.createViews(exclude=EventStorage.viewTableExcludes,show=True)
            storageTableList=EventStorage.getTableList()
            print(f"found {len(storageTableList)} storage Tables for the ConferenceCorpus")
            for baseEntity in ["Event","EventSeries"]:
                plantUml=EventStorage.asPlantUml(baseEntity,exclude=EventStorage.viewTableExcludes)
                print(plantUml)
            profiler.time()
            
            
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 1
    except Exception as e:
        if DEBUG:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        if args.debug:
            print(traceback.format_exc())
        return 2     
        
DEBUG = 0
    
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(main())
