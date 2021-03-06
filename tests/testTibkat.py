from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup
from corpus.event import EventStorage
from lodstorage.query import Query
from corpus.datasources.tibkat import Tibkat,TibkatEvent
import datetime
from collections import Counter
import getpass
import sys


class TestTibkatEvents(DataSourceTest):
    '''
    test for TIBKAT datasource
    '''
    
    def setUp(self, debug:bool=False, profile:bool=True, **kwargs):
        '''
        setUp the test environment
        '''
        super().setUp(debug=debug, profile=True, **kwargs)
        self.lookup=None
        user=getpass.getuser()
        if user=="wf":
            forceUpdate=False
            #Tibkat.limitFiles=100
            self.lookup= lookup=CorpusLookup(lookupIds=["tibkat"])
            self.lookup.load(forceUpdate=forceUpdate)
            self.tibkatDataSource=lookup.getDataSource("tibkat")
            self.eventManager=self.tibkatDataSource.eventManager
            self.eventSeriesManager=self.tibkatDataSource.eventSeriesManager
      
    def testTibkat(self):
        '''
        test CrossRef as an event data source
        '''
        if self.lookup is None:
            print("testTibkat not tested",file=sys.stderr)
            return
        expectedEvents=Tibkat.limitFiles*9
        _eventSeriesList,_eventList=self.checkDataSource(self.tibkatDataSource,0,expectedEvents,eventSample="FSE 2003")
    
    def testParseTibkatDescription(self):
        '''
        check the elements of a TIBKat description
        '''
        testSets=[{
            'description': 'Italian Workshop on Neural Nets (WIRN) ; 8 (Vietri) : 1996.05.23-25',
            'acronym': 'WIRN',
            'ordinal': 8,
            'location': 'Vietri',
            'startDate':  datetime.date(1996, 5, 23),
            'endDate': datetime.date(1996, 5, 25)
        },
        {
            'description': 'WALCOM ; 15 (Online) : 2021.02.28-03.02',
            'acronym': 'WALCOM',
            'ordinal': 15,
            'location': 'Online',
            'startDate':  datetime.date(2021, 2, 28),
            'endDate': datetime.date(2021, 3, 2)
        }
        ]
        for testSet in testSets:
            description=testSet["description"]
            parseResult=TibkatEvent.parseDescription(description)
            if self.debug:
                print(parseResult)
            for key in testSet:
                if key!="description":
                    self.assertEqual(testSet[key],parseResult[key])
            pass   
    
    def testDescriptionParsing(self):
        '''
        test description parsing
        '''
        if self.lookup is None:
            print("testDescriptionParsing not tested",file=sys.stderr)
            return
        debug=self.debug
        #debug=True
        sqlDB=EventStorage.getSqlDB()
        limit="LIMIT 50"
        sql=f"""select ppn,description from event_tibkat {limit}"""
        title="TIBKAT acronym handling"
        query=Query(title,sql,lang='sql')
        eventRecords=sqlDB.query(query.query)
        keyCounter=Counter()
        for eventRecord in eventRecords:
            desc=eventRecord["description"]
            if desc is not None:
                parts=desc.split(self.eventManager.listSeparator) # eventManager.listSepator
                for part in parts:
                    parseResult=TibkatEvent.parseDescription(part)
                    #if (debug):
                    #    print(parseResult)
                    for key in parseResult:
                        keyCounter[key]+=1
                    if "startDate" in parseResult and "endDate" in parseResult:
                        startDate=parseResult["startDate"] 
                        endDate=parseResult["endDate"]
                        if startDate>endDate:
                            keyCounter["invalidDateRange"]+=1

        if debug:
            print(keyCounter.most_common())
    