'''
Created on 2020-08-20

@author: wf
'''
import unittest
from corpus.datasources.wikicfp import WikiCfp
from corpus.datasources.wikicfpscrape import WikiCfpScrape,WikiCfpEventFetcher, CrawlType, CrawlBatch
import os
from collections import Counter
import jsonpickle
from datetime import datetime
import corpus.datasources.wikicfpscrape

class TestWikiCFP(unittest.TestCase):
    '''
    test events from WikiCFP
    '''

    def setUp(self):
        self.debug=True
        self.profile=True
        self.wikiCFPDown=True
        pass

    def tearDown(self):
        pass

    def printDelimiterCount(self,names):
        '''
        print the count of the most common used delimiters in the given name list
        '''
        ordC=Counter()
        for name in names:
            if name is not None:
                for char in name:
                    code=ord(char)
                    if code<ord("A"):
                        ordC[code]+=1
        for index,countT in enumerate(ordC.most_common(10)):
            code,count=countT
            print ("%d: %d %s -> %d" % (index,code,chr(code),count))
            
    def testCrawlFilesToJson(self):
        '''
        test getting the crawlFiles content
        '''
        wikiCfp=WikiCfp()
        wikiCfpScrape=wikiCfp.wikiCfpScrape
        expected={
            "Event": 88000,
            "Series": 1000
        }
        for crawlType in CrawlType:
            jsonEm=wikiCfpScrape.crawlFilesToJson(crawlType=crawlType,withStore=False)
            entityList=jsonEm.getList()
            self.assertTrue(len(entityList)>expected[crawlType.value])

    def testCrawledJsonFiles(self):
        '''
        get the crawl files
        '''
        wikiCfp=WikiCfp()
        wikiCfpScrape=wikiCfp.wikiCfpScrape
        expected={
            "Event": 140,
            "Series": 2
        }
        for crawlType in CrawlType:
            crawlFiles=wikiCfpScrape.jsonFiles(crawlType)
            expectedLen=expected[crawlType.value]
            msg=f"found {len(crawlFiles)}wikiCFP {crawlType.value} crawl files .. expecting {expectedLen}" 
            print (msg)
            self.assertTrue(len(crawlFiles)>=expected[crawlType.value],msg)
        
    def testJsonPickleDateTime(self):
        '''
        test the JsonPickle datetime encoding mystery
        
        '''
        d=datetime.fromisoformat("2021-07-31")
        dp=jsonpickle.encode(d)
        if self.debug:
            print(dp)
        d2=jsonpickle.decode(dp)
        self.assertEqual(d,d2)
        

    def testWikiCFP(self):
        '''
        test event handling from WikiCFP
        '''
        wikiCfp=WikiCfp()
        wikiCfpScrape=wikiCfp.wikiCfpScrape
        jsonEm=wikiCfpScrape.cacheToJsonManager(CrawlType.EVENT)
        self.assertTrue(jsonEm.isCached())
        self.assertTrue(len(jsonEm.events)>80000)
        names=[]
        for event in jsonEm.events:
            if hasattr(event, "locality"):
                names.append(event.locality)
        self.printDelimiterCount(names)

        pass

    def testInvalidUrl(self):
        '''
        make sure only valid urls are accepted
        '''
        eventFetcher=WikiCfpEventFetcher(debug=True)
        try:
            eventFetcher.fromUrl("http://google.com")
            self.fail("invalid url should raise an exception")
        except:
            pass

    def testEventScraping(self):
        '''
        test scraping the given event

         test "This item has been deleted" WikiCFP items
        e.g.
        http://www.wikicfp.com/cfp/servlet/event.showcfp?eventid=3
        '''
        eventIds=[3862,1]
        isDeleted=[False,True]
        event=WikiCfpEventFetcher(debug=self.debug)
        try:
            for index,eventId in enumerate(eventIds):
                rawEvent=event.fromEventId(eventId)
                if self.debug:
                    print (rawEvent)
                self.assertTrue(isDeleted[index]==rawEvent['deleted'])
        except Exception as ex:
            self.handleError(ex)    
            
    def testGettingEventSeriesForEvent(self):
        '''
        test extracting the event series id from th event page
        '''
        self.debug=True
        expectedSeriesId=['1769',None]
        eventIds=[1974,139964]
        event=WikiCfpEventFetcher(debug=self.debug,timeout=3.5)
        try:
            for index,eventId in enumerate(eventIds):
                rawEvent=event.fromEventId(eventId)
                expected=expectedSeriesId[index]
                if expected:
                    self.assertEqual(expected,rawEvent['seriesId'])
                else:
                    self.assertTrue('seriesId' not in rawEvent)
                if self.debug:
                    print (f"{index}:{rawEvent}")
        except Exception as ex:
            self.handleError(ex)
            
    def testGettingLatestEvent(self):
        '''
        get the latest event Id with a binary search
        '''
        #latestEvent=WikiCFPEventFetcher.getLatestEvent(showProgress=True)
        pass
    
    def testCrawlType(self):
        '''
        test CrawlType enumeration
        '''
        for crawlType in CrawlType:
            if self.debug:
                print(crawlType.urlPrefix)
            self.assertTrue(crawlType.urlPrefix.endswith("="))
            crawlBatch=CrawlBatch(1,0,1000,crawlTypeValue=crawlType.value)
            bCrawlType=crawlBatch.crawlType
            self.assertTrue(bCrawlType==crawlType)
            self.assertTrue(bCrawlType is crawlType)
    
    def handleError(self,ex):
        '''
        handle the given exception
        
        Args:
            ex(Exception): the exception to handle
        '''
        if self.wikiCFPDown and "timed out" in str(ex):
            print("WikiCFP is down and we can't do anything about it")
        else:
            raise ex #self.fail(f"{str(ex)}")
    
    def getTempJsonDir(self)->str:
        jsondir=f"/tmp/wikicfp-crawl"
        if not os.path.exists(jsondir):
                    os.makedirs(jsondir)
        return jsondir        
            
    def testCrawlEvents(self):
        '''
        test crawling a few events and storing the result to a json file
        '''
        jsondir=self.getTempJsonDir()
        try: 
            wikicfp=WikiCfp()
            wikiCfpScrape=wikicfp.wikiCfpScrape
            wikiCfpScrape.jsondir=jsondir
            limit=10
            for crawlTypeValue in [CrawlType.SERIES.value,CrawlType.EVENT.value]:
                batch=CrawlBatch(1, 1, limit,crawlTypeValue,None)
                batchEm=wikiCfpScrape.crawl(batch)
                jsonFilePath=batchEm.getCacheFile()
                size=os.stat(jsonFilePath).st_size
                if self.debug:
                    print (f"JSON file for {crawlTypeValue} has size {size}")
                self.assertTrue(size>1400)
                print (f"scraped {len(batchEm.getList())} {crawlTypeValue} records")
        except Exception as ex:
            self.handleError(ex)
            
    def testCrawlEventsViaCommandLine(self):
        '''
        test crawling via commandline
        '''
        jsondir=self.getTempJsonDir()
        for crawlType in [CrawlType.SERIES]:
            args=["--startId", "0", "--stopId", "10","-t", "1", "--targetPath",jsondir,"--crawlType",crawlType.value]
            corpus.datasources.wikicfpscrape.main(args)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
