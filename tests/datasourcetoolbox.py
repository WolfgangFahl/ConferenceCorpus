'''
Created on 2021-07-29

@author: wf
'''
import unittest
from unittest import TestCase
from corpus.eventcorpus import EventDataSource,EventCorpus
from corpus.datasources.dblp import DblpEventManager
import warnings
from lodstorage.lod import LOD
from geograpy.utils import Profiler
import getpass
import os
import sys
import argparse
from pydevd_file_utils import setup_client_server_paths

from corpus.lookup import CorpusLookup


class DataSourceTest(TestCase):
    '''
    test for EventDataSources
    '''
    @classmethod
    def main():
        # python, unittest: is there a way to pass command line options to the app
        # https://stackoverflow.com/a/8660290/1497139
        description="EventCorpus DataSource Test"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument('--debugServer',
                                     help="remote debug Server")
        parser.add_argument('--debugPort',type=int,
                                     help="remote debug Port",default=5678)
        parser.add_argument('--debugRemotePath',help="remote debug Server path mapping - remotePath") 
        parser.add_argument('--debugLocalPath',help="remote debug Server path mapping - localPath")
        parser.add_argument('unittest_args', nargs='*')

        args = parser.parse_args()
        DataSourceTest.optionalDebug(args)
        
        # Now set the sys.argv to the unittest_args (leaving sys.argv[0] alone)
        sys.argv[1:] = args.unittest_args
        unittest.main()
        
    @staticmethod    
    def optionalDebug(args):   
        '''
        start the remote debugger if the arguments specify so
        
        Args:
            args(): The command line arguments
        '''
        if args.debugServer:
            import pydevd
            print (f"remotePath: {args.debugRemotePath} localPath:{args.debugLocalPath}",flush=True)
            if args.debugRemotePath and args.debugLocalPath:
                MY_PATHS_FROM_ECLIPSE_TO_PYTHON = [
                    (args.debugRemotePath, args.debugLocalPath),
                ]
                setup_client_server_paths(MY_PATHS_FROM_ECLIPSE_TO_PYTHON)
                    #os.environ["PATHS_FROM_ECLIPSE_TO_PYTHON"]='[["%s", "%s"]]' % (remotePath,localPath)
                    #print("trying to debug with PATHS_FROM_ECLIPSE_TO_PYTHON=%s" % os.environ["PATHS_FROM_ECLIPSE_TO_PYTHON"]);
         
            pydevd.settrace(args.debugServer, port=args.debugPort,stdoutToServer=True, stderrToServer=True)
            print(f"command line args are: {str(sys.argv)}")
 
    def setUp(self,debug=False,profile=True):
        '''
        setUp test environment
        '''
        TestCase.setUp(self)
        self.debug=debug
        msg=(f"test {self._testMethodName} ... with debug={self.debug}")
        # make sure there is an EventCorpus.db to speed up tests
        EventCorpus.download()
        DblpEventManager.cacheOnly=True
        self.profiler=Profiler(msg=msg,profile=profile)
        self.forceUpdate=False
        # make sure unclosed socket warnings are not shown 
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
        #self.longMessage=True
        
    def tearDown(self):
        self.profiler.time()
        pass    
        
    def inCI(self):
        '''
        are we running in a Continuous Integration Environment?
        '''
        publicCI=getpass.getuser() in ["travis", "runner"] 
        jenkins= "JENKINS_HOME" in os.environ
        return publicCI or jenkins
        
    def checkDataSource(self,eventDataSource:EventDataSource, expectedSeries:int,expectedEvents:int,eventSample:str=None):
        '''
        check the given DataSource
        
        Args:
            eventDataSource(EventDataSource): the event data source to check
        '''
        esm=eventDataSource.eventSeriesManager
        esm.configure()
        esm.fromCache(force=self.forceUpdate)
        esl=esm.getList()
        if self.debug:
            print(f"Found {len(esl)} {eventDataSource.name} scientific event Series")
        
        if not esm.isCached() or self.forceUpdate:
            esm.store()
            
        em=eventDataSource.eventManager
        em.configure()
        em.fromCache(force=self.forceUpdate)
        el=em.getList()
        if self.debug:
            print(f"Found {len(el)} {eventDataSource.name} scientific events")
        if not em.isCached():
            em.store()
        msg=f"found {len(esl)} event series"
        self.assertTrue(len(esl)>=expectedSeries,msg)
        msg=f"found {len(el)} events"
        self.assertTrue(len(el)>=expectedEvents,msg)
        eventsByAcronym,_dup=LOD.getLookup(el, "acronym")
        if eventSample is not None:
            event=eventsByAcronym[eventSample]
            print (f"Sample event for {eventDataSource.name}: {len(el)} events {len(esl)} eventseries")
            print (event.toJSON())
        return esl,el

    @staticmethod
    def getEventSeries(seriesAcronym:str):
        """
        Returns the event series as dict of lod (records are categorized into the different data sources)

        Args:
            seriesAcronym: acronym of the series

        Returns:
            dict of lod
        """
        lookup=CorpusLookup()
        multiQuery = "select * from {event}"
        variable = lookup.getMultiQueryVariable(multiQuery)
        idQuery = f"""select source,eventId from event where acronym like "{seriesAcronym.replace('"','')}%" order by year desc"""
        dictOfLod = lookup.getDictOfLod4MultiQuery(multiQuery, idQuery)
        return dictOfLod