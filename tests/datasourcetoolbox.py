'''
Created on 2021-07-29

@author: wf
'''
from unittest import TestCase
from corpus.eventcorpus import EventDataSource

class DataSourceTest(TestCase):
    '''
    test for EventDataSources
    '''
 
    def setUp(self):
        '''
        setUp test environment
        '''
        TestCase.setUp(self)
        self.debug=True
        self.forceUpdate=False
        
    def tearDown(self):
        pass    
        
        
    def checkDataSource(self,eventDataSource:EventDataSource, expectedSeries:int,expectedEvents:int):
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
        self.assertTrue(len(esl)>expectedSeries)
        self.assertTrue(len(el)>expectedEvents)