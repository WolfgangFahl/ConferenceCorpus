'''
Created on 27.07.2021

@author: wf
'''
import unittest
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup
from collections import Counter
from lodstorage.query import Query
import copy

class TestWikiData(DataSourceTest):
    '''
    test wiki data access
    '''

    @classmethod
    def setUpClass(cls):
        super(TestWikiData, cls).setUpClass()
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
        
    def setUp(self):
        DataSourceTest.setUp(self)
        self.lookup=TestWikiData.lookup
        self.wikidataDataSource=TestWikiData.wikidataDataSource
        self.dblpDataSource=TestWikiData.dblpDataSource
        self.wdEm=TestWikiData.wdEm
        self.wdEsm=TestWikiData.wdEsm
        self.dblpEm=TestWikiData.dblpEm
        self.dblpEsm=TestWikiData.dblpEsm
        self.wdDblpSeries=TestWikiData.wdDblpSeries
        self.dblpSeries=TestWikiData.dblpSeries
        self.wdEvents=TestWikiData.wdEvents
        self.dblpEvents=TestWikiData.dblpEvents
        pass
    
    def testWikidata(self):
        '''
        test getting the wikiData Event Series
        '''
        self.checkDataSource(self.wikidataDataSource,4200,7400)
        
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
        print(f"{wdSeries.eventSeriesId}:{len(wdEvents)} - {len(dblpEvents)}")
        for wdEvent in sorted(wdEvents,key=lambda e:e.title):
            ordinal="??" if wdEvent.ordinal is None else f"{int(wdEvent.ordinal):2.0f}"
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
            foundStr="✓" if found  else "❌"
            count[found]+=1
            if found and dblpSeriesId in samples:
                print (f"{dblpSeriesId} {wdSeries.url}- {foundStr}")
                self.checkSample(dblpSeriesId)
        print (msg)
        print (count.most_common())


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()