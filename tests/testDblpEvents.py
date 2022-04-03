'''
Created on 28.07.2021

@author: wf
'''
import tests.testDblpXml
from datetime import datetime
from corpus.datasources.dblp import Dblp
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup


class TestDblpEvents(DataSourceTest):
    '''
    test the dblp data source
    '''
    
    @classmethod
    def setUpClass(cls):
        super(TestDblpEvents, cls).setUpClass()
        cls.debug=False
        cls.mock=tests.testDblpXml.TestDblp.mock 
        cls.lookup=CorpusLookup(lookupIds=["dblp"],configure=cls.configureCorpusLookup)
        cls.lookup.load(forceUpdate=False)
        cls.dblp=Dblp()
 
    def setUp(self, **kwargs):
        '''
        setup 
        '''
        DataSourceTest.setUp(self, **kwargs)
        self.lookup=TestDblpEvents.lookup
        self.dblp=TestDblpEvents.dblp
        pass
    
    @classmethod
    def configureCorpusLookup(cls,lookup:CorpusLookup):
        '''
        callback to configure the corpus lookup
        '''
        dblpDataSource=lookup.getDataSource("dblp")
        dblpXml=tests.testDblpXml.TestDblp.getMockedDblp(mock=cls.mock,debug=cls.debug)
        dblpDataSource.eventManager.dblpXml=dblpXml
        dblpDataSource.eventSeriesManager.dblpXml=dblpXml
        
    def testDblp(self):
        '''
        test getting the conference series and events from dblp xml dump
        '''
      
        dblpDataSource=self.lookup.getDataSource("dblp")
        self.checkDataSource(dblpDataSource, 138 if self.mock else 5200,1000 if self.mock else 40000)    

    def testDblpDateFix(self):
        '''
        test Dblp DateRange extraction/fixing
        '''
        dblpDataSource=self.lookup.getDataSource("dblp")
        limit=100
        for i,dblpEvent in enumerate(dblpDataSource.eventManager.events):
            dateRange=Dblp.getDateRangeFromTitle(dblpEvent.title)
            if self.debug and i < limit:
                print(dateRange)
                
    def testDateRange(self):
        '''
        test date Range parsing
        '''
        testRecords=[
            {
                "rawDate": "18-21 September 2005",
                "startDate": datetime(2005, 9, 18, 0, 0),
                "endDate": datetime(2005, 9, 21, 0, 0),
                "year": 2005
            },
            {
                "rawDate": "18-21st September 2005",
                "startDate": datetime(2005, 9, 18, 0, 0),
                "endDate": datetime(2005, 9, 21, 0, 0),
                "year": 2005
            }
        ]
        for testRecord in testRecords:
            dateRange=Dblp.getDateRange(testRecord["rawDate"])
            if self.debug:
                print(dateRange)
            for key, dateValue in dateRange.items():
                self.assertEqual(testRecord.get(key), dateValue)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    DataSourceTest.main()