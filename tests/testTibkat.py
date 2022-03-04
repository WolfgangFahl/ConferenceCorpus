from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup
from corpus.event import EventStorage
from lodstorage.query import Query
from corpus.datasources.tibkat import TibkatEvent
import datetime

class TestTibkatEvents(DataSourceTest):
    '''
    test for TIBKAT datasource
    '''
    
    def setUp(self):
        super().setUp()
        self.lookup= lookup=CorpusLookup(lookupIds=["tibkat"])
        self.lookup.load(forceUpdate=False)
        self.tibkatDataSource=lookup.getDataSource("tibkat")
        self.eventManager=self.tibkatDataSource.eventManager
        self.eventSeriesManager=self.tibkatDataSource.eventSeriesManager
      
    def testTibkat(self):
        '''
        test CrossRef as an event data source
        '''
       
        _eventSeriesList,_eventList=self.checkDataSource(self.tibkatDataSource,0,88000,eventSample="ISWC 2008")
        pass
    
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
        }
        ]
        debug=True
        for testSet in testSets:
            description=testSet["description"]
            parseResult=TibkatEvent.parseDescription(description)
            if debug:
                print(parseResult)
            for key in testSet:
                if key!="description":
                    self.assertEqual(testSet[key],parseResult[key])
            pass
            
    
    def testAcronyms(self):
        sqlDB=EventStorage.getSqlDB()
        sql="""select ppn,description from event_tibkat"""
        title="TIBKAT acronym handling"
        query=Query(title,sql,lang='sql')
        eventRecords=sqlDB.query(query.query)
        for eventRecord in eventRecords:
            desc=eventRecord["description"]
            if desc is not None:
                parts=desc.split(self.eventManager.listSeparator) # eventManager.listSepator
                for part in parts:
                    parseResult=TibkatEvent.parseDescription(part)
                pass
    