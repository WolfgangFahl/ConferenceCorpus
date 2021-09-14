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
import re
from lodstorage.query import Query
    
class TestGnd(DataSourceTest):
    '''
    test getting conference information from Gemeinsame Normdatei
    '''
    
    def setUp(self):
        super().setUp(debug=True)
        
        
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
        gndDataSource=self.getGndDataSource(forceUpdate=True)
        expected=min(GND.limit,6000)
        self.checkDataSource(gndDataSource,1,expected)
        pass
    
    def setOrganization(self,event,orgStr):
        event.organization=orgStr
    
    def setLocation(self,event,location):
        event.location=location
        
    def setOrdinal(self,event,ordinalStr,counter):
        ordinalStr=ordinalStr.strip()
        m=re.match(r"^([0-9]+)\.?$",ordinalStr)
        if m:
            ordinal=int(m.group(1))
            event.ordinal=ordinal
            pass
        else:
            counter["invalidOrdinal"]+=1
    
    def setYear(self,event,yearStr,counter):
        '''
        set the year of the given event
        '''
        yearStr=yearStr.strip()
        if re.match(r"^[0-9]+$",yearStr):
            event.year=int(yearStr)
            return True
        else:
            if self.debug:
                print(yearStr)
            counter["invalidYear"]+=1
            return False
        
    
    def gndTitleExtract(self,event,counter):
        '''
        extract title information from gnd event
        '''
        regex=r"(.*)\((.*?)\)"
        m=re.match(regex,event.title)
        if m:
            event.title=m.group(1)
            ordYearLocation=m.group(2)
            parts=ordYearLocation.split(":")
            plen=len(parts)
            counter[plen]+=1
            if plen==1:
                self.setYear(event,ordYearLocation,counter)
            elif plen==2:
                self.setYear(event,parts[0],counter)
                self.setLocation(event,parts[1])
            elif plen==3:
                self.setOrdinal(event,parts[0],counter)
                self.setYear(event,parts[1],counter)
                self.setLocation(event,parts[2])
            elif plen==4:
                self.setOrganization(event,parts[0])
                self.setOrdinal(event,parts[1],counter)
                self.setYear(event,parts[2],counter)
                self.setLocation(event,parts[3])
                pass
        else:
            #print(event.title)
            counter["invalid"]+=1
            
    
    def testOrdinal(self):
        '''
        test ordinal analysis
        '''
        gndDataSource=self.getGndDataSource()
        events=gndDataSource.eventManager.events
        counter=Counter()
        for event in events:
            self.gndTitleExtract(event,counter)
        print (counter.most_common())
        
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
order by 1 desc
limit 25"""
        title="GND query duplicates"
        query=Query(title,sql,lang='sql')
        eventRecords=sqlDB.query(query.query)
        dqr=query.documentQueryResult(eventRecords)
        show=True
        if show:
            print(dqr)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()