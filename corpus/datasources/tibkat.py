'''
Created on 2022-02-16

@author: wf
'''
import itertools
from typing import Union

from wikibot.wikipush import WikiPush
from wikifile.wikiFile import WikiFile
from wikifile.wikiFileManager import WikiFileManager

from corpus.datasources.openresearch import OREvent
from corpus.version import Version
import json
import os
import sys
DEBUG = 0
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

class Tibkat:
    '''
    TIBKAT event meta data access
    
    https://www.tib.eu
    
    Technische Informationsbibliothek (TIB)
    
    Public datasets available via
    
    https://tib.eu/data/rdf
    
    '''

    @property
    def debug(self):
        return getattr(self, "_debug", False)

    @debug.setter
    def debug(self, debug:bool):
        setattr(self, "_debug", debug)
    
    def main(self,args):
        '''
        command line access
        '''
        # should take json import and modify target wiki
        self.debug=args.debug
        wikiId = args.target
        # read from stdin
        if args.file is not None:
            path = os.path.abspath(args.file)
            if os.path.isfile(path):
                with open(path, mode="r") as f:
                    rawInput = f.read()
            else:
                print(f"Given file does not exits! ({path})")
                return
        else:
            rawInput = sys.stdin.read()
        data = [json.loads(f"{l}]") for l in rawInput.split("]\n") if l is not None and len(l.strip())>1]
        records = list(itertools.chain(*data))
        stats={}
        total = len(records)
        for i, record in enumerate(records):
            if self.debug:
                print(f"{i}/{total}:\t {record.get('title', '<Has no title>')}")
            pageTitle, ppnId = self.addPpnIdToWiki(wikiId, record, args.dryrun)
            if pageTitle is None:
                continue
            if pageTitle in stats:
                stats[pageTitle] += [ppnId]
            else:
                stats[pageTitle] = [ppnId]
        # print stats
        wikipush = WikiPush(fromWikiId=wikiId)
        wikiUrl = wikipush.fromWiki.wikiUser.url[:-1] + wikipush.fromWiki.wikiUser.scriptPath
        for pageTitle, pnnIds in stats.items():
            if len(pnnIds) == 1:
                print(f"{bcolors.OKGREEN}{pageTitle}({wikiUrl}/) found Id: {pnnIds}{bcolors.ENDC}")
            elif len(pnnIds) > 1:
                print(f"{bcolors.WARNING}{pageTitle}({wikiUrl}/{pageTitle.replace(' ', '_')}) found Ids: {pnnIds}{bcolors.ENDC}")
            else:
                print(f"{bcolors.OKCYAN}{pageTitle}({wikiUrl}/) no id in records {bcolors.ENDC}")



    def addPpnIdToWiki(self, wikiId:str, record:dict, isDryRun:bool=False) -> (str,str):
        """
        tries to find a matching event in the given wiki for the given event records to add the ppnId

        Args:
            wikiId: id of the wiki
            record: event record containing event acronym, ordinal and ppn

        Returns:
            (str, str) (name of the matching page, ppn that was added)
        """
        event = record.get("event", None)
        if event is None:
            return None, None
        eventParts = event.split(";")
        if len(eventParts) < 2:
            return None, None
        seriesAcronym = eventParts[0].strip()
        ordinal = eventParts[-1].strip()
        wikiFile = self.getMatchingEventFromWiki(wikiId, seriesAcronym, ordinal)
        if wikiFile is None:
            return None, None
        else:
            ppnId = record.get("ppn")
            if ppnId is None:
                return wikiFile.getPageTitle(), None
            ppnTemplateName = [r.get("templateParam") for r in OREvent.propertyLookupList if r.get("name") == "TibKatId"][0]
            wikiFile.updateTemplate(OREvent.templateName, args={ppnTemplateName:ppnId}, overwrite=True)
            if not isDryRun:
                wikiFile.pushToWiki("Added TibKatId")
            return wikiFile.getPageTitle(), ppnId

    def getMatchingEventFromWiki(self, wikiId:str, acronym:str, ordinal:int) -> Union[WikiFile, None]:
        """
        retrieves a matching event form the gicven wiki and returns the wikiFile
        Args:
            wikiId: id of the wiki
            acronym: aconym of the event series
            ordinal: ordinal of the event

        Returns:
            WikiFile if a matching event is found otherwise None
        """
        manager = WikiFileManager(sourceWikiId=wikiId, targetWikiId=wikiId)
        query = f"{{{{#ask: [[Event in series::{acronym}]][[Ordinal::{ordinal}]]}}}}"
        qres = list(manager.wikiPush.query(query))
        if qres:
            wikiFile = manager.getWikiFileFromWiki(pageTitle=qres[0])
            return wikiFile
        return None


class bcolors:
    """
    see https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    
    
def main(argv=None): # IGNORE:C0111
    '''main program.'''

    if argv is None:
        argv=sys.argv[1:]
        
    program_name = os.path.basename(__file__)
    program_version = "v%s" % Version.version
    program_build_date = str(Version.updated)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = "script import TIBKat Data into openresearch compatible wiki"
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
        parser.add_argument("-d", "--debug", dest="debug",   action="store_true", help="set debug [default: %(default)s]")
        parser.add_argument("-t", "--target", dest="target", help="target wiki id")
        parser.add_argument("-f", "--file", dest="file", help="file with the data. If not defined read from stdin")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument('--dryrun', action="store_true", dest='dryrun', help="")
        args = parser.parse_args(argv)
        tibkat=Tibkat()
        tibkat.main(args)
     
  
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
