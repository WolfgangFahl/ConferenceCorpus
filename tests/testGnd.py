'''
Created on 05.09.2021

@author: wf
'''
import unittest
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup
from corpus.event import EventStorage
from corpus.datasources.gnd import GND
from collections import Counter
from lodstorage.query import Query
import getpass
import subprocess, platform
    
class TestGnd(DataSourceTest):
    '''
    test getting conference information from Gemeinsame Normdatei
    '''
    
    def setUp(self):
        super().setUp(debug=False)
        
    def pingTest(self,sHost=GND.host):
        # https://stackoverflow.com/a/34455969/1497139
        try:
            option="-n" if platform.system().lower()=="windows" else "-c"
            cmd="ping %s 1 -t 1 %s" % (option,sHost) 
            output = subprocess.check_output(cmd, shell=True)
            return output is not None
        except Exception:
            return False
       
    def available(self):
        '''
        check whether the SPARQL server is available
        '''
        return False
        return getpass.getuser()=="wf" and self.pingTest();
        
        
    def getGndDataSource(self,forceUpdate=False):
        '''
        get the Gemeinsame Normdatei Datasource
        '''
        lookup=CorpusLookup(lookupIds=["gnd"])
        
        lookup.load(forceUpdate=forceUpdate)
        gndDataSource=lookup.getDataSource("gnd")
        return gndDataSource

    def testGnd(self):
        '''
        test getting conference information from Gemeinsame Normdatei
        '''
        gndDataSource=self.getGndDataSource(forceUpdate=False)
        expected=min(GND.limit,700000)
        self.checkDataSource(gndDataSource,1,expected)
        pass
    
    def testQuery(self):
        '''
        '''
        queryMap={"name":"dblp","lang":"sql","query":"""select event,eventId,title,date
from event_gnd
where title like '%Italian Research Conference on Digital Libraries%'"""
        }
        query=Query(**queryMap)
        sqlDB=EventStorage.getSqlDB()
        lod=sqlDB.query(query.query)
        for tablefmt in ["mediawiki","github","latex"]:
            doc=query.documentQueryResult(lod, tablefmt=tablefmt,floatfmt=".0f")
            show=self.debug
            if show:
                docstr=str(doc)
                print(docstr)
    
    def testTitleExtract(self):
        '''
        test ordinal analysis
        '''
        oldDebug=GND.debug
        #GND.debug=True
        gndDataSource=self.getGndDataSource()
        events=gndDataSource.eventManager.events
        counter=Counter()
        for event in events:
            event.titleExtract(counter)
        print (counter.most_common())
        GND.debug=oldDebug
        storeToDatabase=False
        if storeToDatabase:
            gndDataSource.eventManager.store()
        
    def testDateRanges(self):
        '''
        test date range parsing
        '''
        gndDataSource=self.getGndDataSource(forceUpdate=False)
        events=gndDataSource.eventManager.events
        debug=self.debug
        #debug=True
        minTotal=len(events)
        invalid=0
        for i,event in enumerate(events):
            dateRange=(GND.getDateRange(event.date))
            if (len(dateRange)==0 and event.date is not None):
                invalid+=1
                if debug:
                    print("%5d: %s: %s %s" % (i,event.eventId,event.date,dateRange))
        if debug:
            print("%d GND dates are invalid " % invalid)
        self.assertTrue(invalid<minTotal/300)
        
        
    def testStats(self):
        '''
        test statistics
        '''
        EventStorage.withShowProgress=True
        _gndDataSource=self.getGndDataSource()
        sqlDB=EventStorage.getSqlDB()
        sql="""select count(*) as count,title,event 
from event_GND
group by title 
having count(*)>1
order by 1 desc
"""
        title="GND query duplicates"
        query=Query(title,sql,lang='sql')
        eventRecords=sqlDB.query(query.query)
        duplicates=0
        for eventRecord in eventRecords:
            duplicates+=int(eventRecord["count"])
        msg=f"found {duplicates} duplicates for {len(eventRecords)} duplicate titles"
        print(msg)
        # TODO
        # activate test for new version
        self.assertTrue(duplicates<2500)
        show=False
        limit=5
        dqr=query.documentQueryResult(eventRecords,limit=limit)
        
        if show:
            print(dqr)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()