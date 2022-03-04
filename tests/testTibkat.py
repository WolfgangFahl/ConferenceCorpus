from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup

class TestTibkatEvents(DataSourceTest):
    '''
    test for TIBKAT datasource
    '''

    def testTibkat(self):
        '''
        test CrossRef as an event data source
        '''
        lookup=CorpusLookup(lookupIds=["tibkat"])
        lookup.load(forceUpdate=True)
        tibkatDataSource=lookup.getDataSource("tibkat")
        _eventSeriesList,_eventList=self.checkDataSource(tibkatDataSource,0,10000,eventSample="ISWC 2008")
        pass
    