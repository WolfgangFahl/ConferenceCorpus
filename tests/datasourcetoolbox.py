'''
Created on 2021-07-29

@author: wf
'''
from unittest import TestCase
from corpus.eventcorpus import EventDataSource,EventCorpus
from corpus.datasources.dblp import DblpEventManager
import warnings
from lodstorage.lod import LOD
from geograpy.utils import Profiler
import getpass
import os

from corpus.lookup import CorpusLookup


class DataSourceTest(TestCase):
    '''
    test for EventDataSources
    '''
 
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