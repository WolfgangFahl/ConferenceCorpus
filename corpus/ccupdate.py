'''
Created on 2022-03-05

@author: wf
'''
import os
import sys
import traceback
from lodstorage.lod import LOD
from corpus.version import Version
from corpus.lookup import CorpusLookup
from corpus.locationfixer import LocationFixer
from corpus.datasources.dblpxml import DblpXml
from corpus.datasources.tibkat import Tibkat
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

class ConferenceCorpusUpdate():
    def __init__(self,lookupId):
        '''
        constructor
        '''
        self.lookupId=lookupId
        
    def updateDataSource(self,source,sampleId:str=None):
        '''
        update the given DataSource
        '''
        print(f"updating conference corpus database from {source}")
        lookup=CorpusLookup(lookupIds=[self.lookupId])
        lookup.load(forceUpdate=True)
        eventDataSource=lookup.getDataSource(self.lookupId)
        el=eventDataSource.eventManager.getList()
        esl=eventDataSource.eventSeriesManager.getList()
        msg=f"{eventDataSource.name}: {len(el)} events {len(esl)} eventseries"
        print(msg)
        eventsByAcronym,_dup=LOD.getLookup(el, "acronym")
        if sampleId is not None:
            if sampleId in eventsByAcronym:
                event=eventsByAcronym[sampleId]
                print (event.toJSON())
            else:
                print(f"sample event id {sampleId} not found")
       
    
class TibkatUpdater(ConferenceCorpusUpdate):
    '''
    update for Tikbat data from FTX XML dump
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
        debug=args.debug
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
    program_shortdesc = "dblp xml handling from command line"
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
        parser.add_argument("-dblp","--dblp", dest="dblp",   action="store_true", help="update dblp")
        parser.add_argument("--tibkat", action="store_true",help="update tibkat from ftx")
        parser.add_argument("--fixlocations",nargs="+",help="fix the locations for the given lookup Ids")
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
        if args.dblp:
            dblpUpdater=DblpUpdater()
            dblpUpdater.update(args)
        if args.tibkat:
            tibkatUpdater=TibkatUpdater()
            tibkatUpdater.update(args)
        if args.fixlocations:
            locationFixer=LocationFixer()
            locationFixer.fixLocations4LookupId(args.fixlocations)
        if args.updateSource:
            for lookupId in args.updateSource:
                updater=ConferenceCorpusUpdate(lookupId)
                updater.updateDataSource(f"{lookupId} cache", args.sample)
            
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
