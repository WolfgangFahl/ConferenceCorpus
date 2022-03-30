'''
Created on 04.12.2021

@author: wf
'''
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup
from collections import Counter
from lodstorage.query import Query
import copy


class TestWikiDataDblpMatch(DataSourceTest):
    '''
    test wiki data access with dblp match
    '''

    @classmethod
    def setUpClass(cls):
        super(TestWikiDataDblpMatch, cls).setUpClass()
        cls.lookup=CorpusLookup(lookupIds=["wikidata","dblp"])
        cls.lookup.load(forceUpdate=False)
        cls.wikidataDataSource=cls.lookup.getDataSource("wikidata")
        cls.dblpDataSource=cls.lookup.getDataSource("dblp")
        cls.wdEm=cls.wikidataDataSource.eventManager
        cls.wdEsm=cls.wikidataDataSource.eventSeriesManager
        cls.dblpEm=cls.dblpDataSource.eventManager
        cls.dblpEsm=cls.dblpDataSource.eventSeriesManager
        cls.wdDblpSeries,_dup=cls.wdEsm.getLookup("DBLP_pid")
        cls.dblpSeries,_dup=cls.dblpEsm.getLookup("eventSeriesId")
        cls.wdEvents=cls.wdEm.getLookup("eventInSeriesId",withDuplicates=True)
        cls.dblpEvents=cls.dblpEm.getLookup("series",withDuplicates=True)
        
    def setUp(self, debug:bool=False, profile:bool=True, **kwargs):
        cls=self.__class__
        DataSourceTest.setUp(self, debug=debug, profile=profile, **kwargs)
        self.lookup=cls.lookup
        self.wikidataDataSource=cls.wikidataDataSource
        self.dblpDataSource=cls.dblpDataSource
        self.wdEm=cls.wdEm
        self.wdEsm=cls.wdEsm
        self.dblpEm=cls.dblpEm
        self.dblpEsm=cls.dblpEsm
        self.wdDblpSeries=cls.wdDblpSeries
        self.dblpSeries=cls.dblpSeries
        self.wdEvents=cls.wdEvents
        self.dblpEvents=cls.dblpEvents
        pass
    
    def showQuery(self,name,sqlQuery,show=True):
        query=Query(name=name,query=sqlQuery,lang='sql')
        qlod=self.lookup.getLod4Query(query.query)
        prefix="https://confident.dbis.rwth-aachen.de/or/index.php?title="
        for tablefmt in ["mediawiki","github","latex"]:
            lod=copy.deepcopy(qlod)
            query.prefixToLink(lod, prefix, tablefmt)
            qdoc=query.documentQueryResult(lod,tablefmt=tablefmt)
            if show:
                print(qdoc)
                  
    def checkSample(self,dblpSeriesId):
        '''
        '''
        dblpSeries=self.dblpSeries[dblpSeriesId]
        wdSeries=self.wdDblpSeries[f"conf/{dblpSeriesId}"]
        wdEvents=self.wdEvents[wdSeries.eventSeriesId]
        dblpEvents=self.dblpEvents[dblpSeriesId]
        if self.debug:
            print(f"{wdSeries.eventSeriesId}:{len(wdEvents)} - {len(dblpEvents)}")
        for wdEvent in sorted(wdEvents,key=lambda e:e.title):
            ordinal="??" if wdEvent.ordinal is None else f"{int(wdEvent.ordinal):2.0f}"
            if self.debug:
                print (f"{ordinal}:{wdEvent.url} {wdEvent.title}")
        sqlQuery=f"""select ordinal,year,title,url from event_wikidata 
where eventInSeriesId="{wdSeries.eventSeriesId}"
order by year"""
        self.showQuery(name=f"dblp Event Series {dblpSeriesId}",sqlQuery=sqlQuery)
        pass
        
    def testSeries(self):
        '''
        test EventSeries from wikidata against dblp series
        '''
        msg=f"found {len(self.wdDblpSeries.keys())} dblp series in wikidata"
        count=Counter()
        samples=["www"]
        for dblpSeriesId in self.wdDblpSeries.keys():
            wdSeries=self.wdDblpSeries[dblpSeriesId]
            dblpSeriesId=dblpSeriesId.replace("conf/","")
            found=dblpSeriesId in self.dblpSeries
            foundStr="✓" if found else "❌"
            count[found]+=1
            if found and dblpSeriesId in samples:
                print(f"{dblpSeriesId} {wdSeries.url}- {foundStr}")
                self.checkSample(dblpSeriesId)
        print(msg)
        print(count.most_common())


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    DataSourceTest.main()