'''
Created on 2022-03-04

@author: wf
'''
import itertools
from wikibot3rd.wikipush import WikiPush
from wikifile.wikiFile import WikiFile
from wikifile.wikiFileManager import WikiFileManager

from corpus.datasources.openresearch import OREvent
from corpus.version import Version
import json
import os
import sys
DEBUG = 1
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from corpus.xmlhandler.xmlparser import XMLEntityParser, XmlEntity
from typing import Iterator, Union
from corpus.utils.progress import Progress


class FTXParser(object):
    '''
    an specialized XML parser for FTX dump files
    '''
    
    def __init__(self,basepath:str):
        '''
        constructor
        
        Args:
            basepath(str): the root of the FTX dump directory
        '''
        self.basepath=basepath
        
    def ftxXmlFile(self,xmlFile:str)->str:
        '''
        Args: 
            xmlFile(str): the name of the FTX XML file 
            
        Returns:
            str: the full path
        
        '''
        path=f"{self.basepath}/{xmlFile}"
        return path
        
    def ftxXmlFiles(self)->list:
        '''
        get the relevant XML files list
        '''
        files = os.listdir(self.basepath)
        files = [f for f in files if f.endswith(".xml")]
        return files
    
    def parse(self,xmlFile,local:bool=True,progress:Progress=None)->Iterator[XmlEntity]:
        '''
          parse the xml data of  volume with the given collectionId
          
          Args:
            xmlFile(str): the file to process
            local(bool): True if the xmlFile name is a local file name
        '''    
        recordTag="{http://www.openarchives.org/OAI/2.0/}document"
        namespaces={'ns0':'http://www.openarchives.org/OAI/2.0/',
                    'ns2': 'http://purl.org/dc/terms/',
                    'dc':'http://purl.org/dc/elements/1.1/'
        }
        xmlPropertyMap= {
            "databaseDate": './ns0:systemInfo/ns0:databaseDate',
            "changeDate": './ns0:systemInfo/ns0:changeDate',
            "ftxCreationDate": './ns0:systemInfo/ns0:ftxCreationDate',
            # formalInfo
            "documentGenreCode": './ns0:formalInfo//ns0:documentGenreCode',
            "documentTypeCode": './ns0:formalInfo//ns0:documentTypeCode',
            # identifiers
            "documentId": './ns0:systemInfo/ns0:documentID',
            "ppn": './/ns0:identifiers/ns0:identifier[@type="ppn"]',
            "firstid": './/ns0:identifiers/ns0:identifier[@type="firstid"]',
            "isbn": './/ns0:identifiers/ns0:identifier[@type="isbn"]',
            "isbn13": './/ns0:identifiers/ns0:identifier[@type="isbn13"]',
            "ean": './/ns0:identifiers/ns0:identifier[@type="ean"]',
            "doi": './/ns0:identifiers/ns0:identifier[@type="doi"]',
            # from corporate creators
            # check for type not existing to get gnd ID
            # https://stackoverflow.com/a/13807791/1497139
            "corporateCreatorTypes@type": './/ns0:corporateCreator',
            "corporateCreatorNames": './/ns0:corporateCreator//ns0:name',
            "gndIds": './/ns0:corporateCreator/ns0:corporateIDs/ns0:corporateID[@type="gnd"]',
            "authorGndId": './/ns0:corporateCreator[@type="author"]/ns0:corporateIDs/ns0:corporateID[@type="gnd"]',
            "sponsorGndId": './/ns0:corporateCreator[@type="sponsor"]/ns0:corporateIDs/ns0:corporateID[@type="gnd"]',
            # bibliographic info
            "title": './ns0:bibliographicInfo/dc:title',
            "alternativeTitles": './ns0:bibliographicInfo/ns0:alternativeTitles/ns2:alternative',
            # conferenceInfo
            "event":  './/ns0:conferenceInfo/ns0:name',
            "location": './/ns0:conferenceInfo/ns0:places/ns0:place',
            "dates":  './/ns0:conferenceInfo/ns0:dates/dc:date',
            "description": './/ns0:conferenceInfo/dc:description',
            "pubyear": './ns0:bibliographicInfo/ns0:publicationInfo/ns2:issued',
            "pubplace": './ns0:bibliographicInfo/ns0:publicationInfo/ns0:publicationPlaces/ns0:publicationPlace',
            # "pubcountry": './ns0:bibliographicInfo/ns0:publicationInfo/ns0:publicationCountries/ns0:publicationCountry', # code Attribute
            "publisher": './ns0:bibliographicInfo/ns0:publicationInfo/dc:publisher',
            # journalInfo
            "journalTitle": './/ns0:journalInfo/dc:title',
            "journalVolumeNumber": './/ns0:journalInfo/ns0:volumeNumber',
            # classification Info
            "bk": "./ns0:classificationInfo/ns0:classifications/ns0:classification[@classificationName='bk']/ns0:code",
            "ddc": "./ns0:classificationInfo/ns0:classifications/ns0:classification[@classificationName='ddc']/ns0:code"
        }        
        if local:
            xmlPath=self.ftxXmlFile(xmlFile)
        else:
            xmlPath=xmlFile
        if os.path.exists(xmlPath):
            xmlParser=XMLEntityParser(xmlPath,recordTag)
            for xmlEntity in xmlParser.parse(xmlPropertyMap,namespaces):
                yield(xmlEntity)
                if progress is not None:
                    progress.next()


class TibkatCmdLine:
    '''
    TIB Kat command line 
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
        data = json.loads(rawInput)
        records = data
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
        retrieves a matching event form the given wiki and returns the wikiFile
        Args:
            wikiId: id of the wiki
            acronym: acronym of the event series
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
        tibkatCmd=TibkatCmdLine()
        tibkatCmd.main(args)
     
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
