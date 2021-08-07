"""
Created on 2020-08-20


  script to read event metadata from http://wikicfp.com
  
  use: python3 wikicfp.py [startId] [stopId] [threads]
  @param startId
  @param stopId
  @param threads - number of threads the script should create to improve performance
  
  example: python3 wikicfp.py --startId 2000 --stopId 2999 10

  @author:     svantje, wf
  @copyright:  2020-2021 TIB Hannover, Wolfgang Fahl. All rights reserved.

"""
import datasources.wikicfp 
from datasources.webscrape import WebScrape
from corpus.event import EventStorage
import datetime
from enum import Enum
import glob
import re
import os
import sys
import threading
import time
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from lodstorage.jsonpicklemixin import JsonPickleMixin
import jsonpickle

class CrawlType(Enum):
    '''
    possible supported storage modes
    '''
    EVENT = "Event"      
    SERIES = "Series"
    
    @property
    def urlPrefix(self):
        baseUrl="http://www.wikicfp.com/cfp"
        if self==CrawlType.EVENT:
            url= f"{baseUrl}/servlet/event.showcfp?eventid="
        elif self==CrawlType.SERIES:
            url= f"{baseUrl}/program?id="
        return url
    
    @classmethod
    def valueMap(cls)->dict:
        '''
        get my list of values
        
        Return:
            list: the list of values
        '''
        valueMap={}
        for c in cls:
            valueMap[c.value]=c
        return valueMap
 
    @classmethod
    def isValid(cls,value:str)->bool:
        '''
        check whether the given value is valid
        
        Args:
            value(str): the value to check
        
        Return:
            bool: True if the value is a valid value of this enum
        '''
        valueMap=cls.valueMap()
        return value in valueMap

class CrawlBatch(object):
    '''
    describe a batch of pages to fetch metadata from
    '''
    
    def __init__(self,threads:int,startId:int,stopId:int,crawlTypeValue:str,threadIndex=None,):
        '''
        construct me with the given number of threads, startId and stopId
        
        Args:
           threads(int): number of threads to use
           startId(int): id of the event to start crawling with
           stopId(int): id of the event to stop crawling
           crawlTypeValue(str): the type of crawling (Event or Series)
           threadIndex(int): the index of this batch
        '''
        self.threads=threads
        self.threadIndex=threadIndex
        self.startId=startId
        self.stopId=stopId     
        if startId <= stopId: 
            self.step = +1
            self.total = stopId-startId+1
        else: 
            self.step = -1
            self.total = startId-stopId+1
        self.batchSize = self.total // threads
        if not CrawlType.isValid(crawlTypeValue):
            raise Exception(f"Invalid crawlType {crawlTypeValue}")
        self.crawlType=CrawlType.valueMap()[crawlTypeValue]
        
    def split(self)->list:
        '''
        split me for my threads
        '''
        crawlBatches=[]
        for threadIndex in range(self.threads):
            s = self.startId + threadIndex * self.batchSize
            e = s + self.batchSize-1
            splitBatch=CrawlBatch(1,s, e,self.crawlType.value,threadIndex)
            crawlBatches.append(splitBatch)
        return crawlBatches
      
    
    def __str__(self):
        '''
        get my string representation
        Return
            str: my string representation
        '''
        text=f"WikiCFP {self.crawlType.value} IDs {self.startId} - {self.stopId} ({self.threads} threads of {self.batchSize} IDs each)"
        return text
 
class WikiCfpScrape(object):
    '''
    support events from http://www.wikicfp.com/cfp/
    '''

    def __init__(self,config=None,debug:bool=False,jsondir:str=None,limit=200000,batchSize=1000,showProgress=True):
        '''
        Constructor
        
        Args:
            config(StorageConfig): the storage configuration to use
            debug(bool): if True debug for crawling is on
            limit(int): maximum number of entries to be crawled
            batchSize(int): default size of batches
            showProgress(bool): if True show Progress
        '''
        self.debug=debug
        self.limit=limit
        self.batchSize=batchSize
        self.showProgress=showProgress
        self.em=self.getEventManager(config)
        self.profile=self.em.config.profile
        if jsondir is not None:
            self.jsondir=jsondir
        else:
            cachePath=self.em.config.getCachePath()
            self.jsondir=f"{cachePath}/wikicfp"
            if not os.path.exists(self.jsondir):
                    os.makedirs(self.jsondir)
        
    def getEventManager(self,config=None,mode='sql'):
        '''
        get an EventManager
        
        Args:
            config(StorageConfig): the storage configuration to use
            mode(string): the storage mode to use e.g. "json" - will select a config based on mode if config is None
        '''
        if config is None:
            config=EventStorage.getStorageConfig(self.debug, mode)
        em=datasources.wikicfp.WikiCfpEventManager(config=config)
        return em
    
    def cacheEvents(self):
        '''
        cache my events to my eventmanager
        '''
        jsonEm=self.getEventManager(mode='json')
        if jsonEm.isCached():
            jsonEm.fromStore()
        else:    
            self.crawlFilesToJson(jsonEm)
        for event in jsonEm.events:
            self.em.events.append(event)
        self.em.store(limit=self.limit, batchSize=self.batchSize)    
        
    def crawlFilesToJson(self,jsonEm):    
        '''
        convert the crawlFiles to Json
        
        Args:
            jsonEm(EventManager): the JSON - storage based Eventmanager to use to collect the results
        '''
        # crawling is not done on startup but need to be done
        # in command line mode ... we just collect the json crawl result files here
        #self.crawl(startId=startId,stopId=stopId)
        startTime=time.time()
        jsonFiles=self.jsonFiles()
        if len(jsonFiles)==0:
            if self.profile or self.debug:
                print("No wikiCFP crawl json backups available")
                
        else:
            for jsonFilePath in jsonFiles:
                #batchEm=self.getEventManager(mode='jsonpickle')
                # legacy mode -file were created before ORM Mode
                # was available - TODO: make new files available in ORM mode with jsonable
                jsonPickleEm=JsonPickleMixin.readJsonPickle(jsonFileName=jsonFilePath,extension='.json')
                jsonPickleEvents=jsonPickleEm['events']
                if self.showProgress:
                    print("%4d: %s" % (len(jsonPickleEvents),jsonFilePath))
                for rawEvent in jsonPickleEvents.values():
                    event=datasources.wikicfp.WikiCfpEvent()
                    if 'title' in rawEvent and rawEvent['title'] is not None:
                        for field in rawEvent:
                            value=rawEvent[field]
                            # workaround:
                            # check jsonpickle __reduce__ values
                            if isinstance(value,dict):
                                # we need something like
                                # {"py/object": "datetime.datetime", "__reduce__": [{"py/type": "datetime.datetime"}, ["B+UHHwAAAAAAAA=="]]}
                                jsonValue=str(value).replace("'", '"')
                                dvalue=jsonpickle.decode(jsonValue)
                                value=dvalue
                            # make sure we ignore field like "py/object"
                            if not "py/" in field:
                                setattr(event,field,value)
                        event.source="wikicfp"
                        for field in ['startDate','endDate','locality','Submission_Deadline','Notification_Due','year']:
                            if not field in rawEvent:
                                setattr(event,field,None)
                        if event.startDate is not None:
                            event.year=event.startDate.year
                        event.url=WikiCfpEventFetcher.getUrl(event.wikiCFPId)
                        jsonEm.events.append(event)
            if self.profile:
                print ("read %d events in %5.1f s" % (len(jsonEm.events),time.time()-startTime))
            jsonEm.store(limit=self.limit,batchSize=self.batchSize)
        
    def jsonFiles(self):  
        '''
        get the list of the json files that have my data
        '''
        jsonFiles=sorted(glob.glob(f"{self.jsondir}/wikicfp_*.json"),key=lambda path:int(re.findall(r'\d+',path)[0]))
        return jsonFiles    
        
    def getJsonFileName(self,crawlBatch):
        '''
        get my the JsonFileName 
        
        Args:
            crawlBatch(CrawlBatch): the batch to crawl):
            
        Return:
            str: the json file name for this batch
        '''
        jsonFilePath=f"{self.jsondir}/wikicfp_{crawlBatch.crawlType.value}{crawlBatch.startId:06d}-{crawlBatch.stopId:06d}.json"
        return jsonFilePath
    
    def getBatchEntityManager(self,crawlBatch:CrawlBatch):
        '''
        get the batch Entity Manager for the given crawlBatch
        
        Args:
            crawlBatch(CrawlBatch): the batch to crawl):
            
        Return:
            EntityManager: either a Event or a Series Manager
        '''
        jsonFilepath=self.getJsonFileName(crawlBatch)
        config=EventStorage.getStorageConfig(debug=self.debug, mode="json")
        config.cacheFile=jsonFilepath
        crawlType=crawlBatch.crawlType
        if crawlType==CrawlType.EVENT:
            batchEm=datasources.wikicfp.WikiCfpEventManager(config=config)
        elif crawlType==CrawlType.SERIES:
            batchEm=datasources.wikicfp.WikiCfpEventSeriesManager(config=config)
        return batchEm
        
    def crawl(self,crawlBatch:CrawlBatch):
        '''
        see https://github.com/TIBHannover/confIDent-dataScraping/blob/master/wikicfp.py
        
        Args:
            crawlBatch(CrawlBatch): the batch to crawl
        '''
       
        print(f'crawling {crawlBatch}')
        batchEm=self.getBatchEntityManager(crawlBatch)
 
        # get all ids
        crawlType=crawlBatch.crawlType
        for eventId in range(int(crawlBatch.startId), int(crawlBatch.stopId+1), crawlBatch.step):
            wEvent=WikiCfpEventFetcher(crawlType=crawlType)
            retry=1
            maxRetries=3
            retrievedResult=False
            while not retrievedResult:
                try:
                    rawEvent=wEvent.fromEventId(eventId)
                    if crawlType == CrawlType.EVENT:
                        event=datasources.wikicfp.WikiCfpEvent()
                        event.fromDict(rawEvent)
                        title="? deleted: %r" %event.deleted if not 'title' in rawEvent else event.title
                        batchEm.getList().append(event)
                    elif crawlType == CrawlType.SERIES:
                        eventSeries=datasources.wikicfp.WikiCfpEventSeries()
                        eventSeries.fromDict(rawEvent)
                        title="?" if not 'title' in rawEvent else eventSeries.title
                        batchEm.getList().append(eventSeries)
                    retrievedResult=True
                except Exception as ex:
                    if "HTTP Error 500" in str(ex):
                        print(f"{eventId} inaccessible due to HTTP Error 500")
                        retrievedResult=True
                    elif "timed out" in str(ex):
                        print(f"{eventId} access timed Out on retry attempt {retry}")
                        retry+=1
                        if retry>maxRetries:
                            raise ex
                    else:
                        raise ex
                    pass
                
            print(f"{eventId:06d}: {title}")
           
           
        batchEm.store()
        return batchEm
            
    def threadedCrawl(self,crawlBatch:CrawlBatch):
        '''
        crawl with the given number of threads, startId and stopId
        
        Args:
            crawlBatch(CrawlBatch): the batch to crawl
        '''
        # determine the eventId range for each threaded job
        startTime=time.time()
        
        msg=f'Crawling {crawlBatch}'
        print(msg)

        # this list will contain all threads -> we can wait for all to finish at the end
        jobs = []

        # now start each thread with its id range and own filename
        for crawlBatch in crawlBatch.split(): 
        
            thread = threading.Thread(target = self.crawl, args=(crawlBatch,))
            jobs.append(thread)
            
        for job in jobs:
            job.start()   

        # wait till all threads have finished before print the last output
        for job in jobs:
            job.join()

        if self.debug:
            elapsed=time.time()-startTime
            print(f'crawling done after {elapsed:5.1f} s')
               
      
class WikiCfpEventFetcher(object):
    '''
    a single WikiCfpEentFetcher to fetch and event or series
    '''
    def __init__(self,crawlType=CrawlType.EVENT,debug=False,showProgress:bool=True,timeout=20):
        '''
        construct me
        
        Args:
            showProgress(bool): if True show progress
            timeout(float): the default timeout
        
        '''
        self.debug=debug
        self.crawlType=crawlType
        self.showProgress=showProgress
        self.progressCount=0
        self.timeout=timeout
            
    def fromTriples(self,rawEvent,triples): 
        '''
        get the rawEvent dict from the given triple e.g.:
        
        v:Event(v:summary)=IDC 2009
        v:Event(v:eventType)=Conference
        v:Event(v:startDate)=2009-06-03T00:00:00
        v:Event(v:endDate)=2009-06-05T23:59:59
        v:Event(v:locality)=Milano, Como, Italy
        v:Event(v:description)= IDC  2009 : The 8th International Conference on Interaction Design and Children
        v:Address(v:locality)=Milano, Como, Italy
        v:Event(v:summary)=Submission Deadline
        v:Event(v:startDate)=2009-01-19T00:00:00
        v:Event(v:summary)=Notification Due
        v:Event(v:startDate)=2009-02-20T00:00:00
        v:Event(v:summary)=Final Version Due
        v:Event(v:startDate)=2009-03-16T00:00:00
        '''
        recentSummary=None
        for s,p,o in triples:
            s=s.replace("v:","")
            p=p.replace("v:","")
            if self.debug:
                print ("%s(%s)=%s" % (s,p,o)) 
            if recentSummary in ['Submission Deadline','Notification Due','Final Version Due']:             
                key=recentSummary.replace(" ","_")
            else:
                key=p 
            if p.endswith('Date'):
                dateStr=o
                if dateStr=="TBD":
                    o=None
                else:    
                    o=datetime.datetime.strptime(
                        dateStr, "%Y-%m-%dT%H:%M:%S").date()
            if not key in rawEvent: 
                rawEvent[key]=o    
            if p=="summary": 
                recentSummary=o 
            else: 
                recentSummary=None
                
    @staticmethod       
    def getUrl(cfpid,crawlType:CrawlType=CrawlType.EVENT)->str:
        '''
        Args:
            cfpid(int): the WikiCFP id of the event or series
            crawlType(CrawlType): Event or Series
            
        Returns:
            the WikiCfP url
        '''
        url=f"{crawlType.urlPrefix}{cfpid}"
        return url   
    
    @classmethod
    def getLatestEvent(cls,debug=False,showProgress=True):
        '''
        get the latest Event doing a binary search
        '''
        wikicfp=WikiCfpEventFetcher(debug,showProgress=showProgress)
        wikicfp.progressCount=0
        wikicfp.getLatesEvetFromPair()
        
    def getHighestNonDeletedIdInRange(self,fromId:int,toId:int)->int:
        '''
        get the event with the highest id int the range fromId to toId that is not deleted
        
        Args:
            fromId(int): minimum id to search from
            toId(int): maximum id to search to
            
        Returns:
            int: maxium id of an event that is not deleted or None if there is none in this range
        '''
        maxId=None
        for eventId in range(fromId,toId+1):
            if self.showProgress:
                print(".",end='',flush=True)
                self.progressCount+=1
                if self.progressCount % 50 == 0:
                    print(flush=True)
            rawEvent=self.fromEventId(eventId)
            if not rawEvent['deleted']:
                maxId=eventId
        return maxId
    
    def getLatesEvetFromPair(self,low=5000,high=300000,margin=40):
        '''
        get the latest Event doing a binary search
        
        Args:
            low(int): lower index to search from
            hight(int): upper index boundary
        '''
        if high-low>margin+1:
            mid=(high+low)//2
            midId=(self.getHighestNonDeletedIdInRange(mid-margin, mid))
            if midId:
                return self.getLatesEvetFromPair(mid+1,high)
            else:
                return self.getLatesEvetFromPair(low, mid-1)
        else:
            return mid
        pass
                           
    def fromEventId(self,cfpid:int):
        '''
        see e.g. https://github.com/andreeaiana/graph_confrec/blob/master/src/data/WikiCFPCrawler.py
        
        Args:
            cfpid(int): the wikicfp id to use
        '''
        url=WikiCfpEventFetcher.getUrl(cfpid,self.crawlType)
        return self.fromUrl(url)
    
    def rawEventFromWebScrape(self,rawEvent:dict,triples:list,scrape:WebScrape):
        '''
        fill the given rawEvent with the data derived from the scrape 
        
        Args:
            rawEvent(dict): the event dictionary
            triples(list): the triples found
            scrape(WebScrape): the webscrape object to be used for parsing
        '''
        if len(triples)==0:
            #scrape.printPrettyHtml(scrape.soup)
            firstH3=scrape.fromTag(scrape.soup, 'h3')
            if "This item has been deleted" in firstH3:
                rawEvent['deleted']=True
        else:        
            self.fromTriples(rawEvent,triples)
            # add series information
            # Tag: <a href="/cfp/program?id=1769&amp;s=ISWC&amp;f=International Semantic Web Conference">International Semantic Web Conference</a>
            m,seriesText=scrape.findLinkForRegexp(r'/cfp/program\?id=([0-9]+).*')
            if m:
                seriesId=m.group(1)
                rawEvent['seriesId']=seriesId
                rawEvent['series']=seriesText
                pass
                
            if 'summary' in rawEvent:
                rawEvent['acronym']=rawEvent.pop('summary').strip()
            if 'description' in rawEvent:
                rawEvent['title']=rawEvent.pop('description').strip()
                
    def rawEventSeriesFromWebScrape(self,rawEvent:dict,scrape:WebScrape):
        '''
        fill the given rawEventSeries with the data derived from the scrape 
        
        Args:
            rawEvent(dict): the event dictionary
            scrape(WebScrape): the webscrape object to be used for parsing
        '''
        title=scrape.soup.find("title")
        if title:
            rawEvent["title"]=title.text.strip()
        dblpM,_text=scrape.findLinkForRegexp(r'http://dblp.uni-trier.de/db/(conf/[a-z0-9]+)/index.html')
        if dblpM:
            dblpSeriesId=dblpM.group(1)
            rawEvent['dblpSeriesId']=dblpSeriesId
        
         
        pass
 
    
    def fromUrl(self,url:str)->dict:
        '''
        get the event form the given url
        
        Args:
            url(str): the url to get the event from
        
        Returns:
            dict: a raw event dict or None if an error occured
        
        '''
        regexp=r"^"+self.crawlType.urlPrefix.replace("?","\?")+"(\d+)$"
        m=re.match(regexp,url)
        if not m:
            raise Exception("Invalid URL %s" % (url))
        else:
            cfpId=int(m.group(1))
        rawEvent={}
        if self.crawlType==CrawlType.EVENT:
            rawEvent['eventId']=f"{cfpId}" 
        else:
            rawEvent['seriesId']=f"{cfpId}" 
        rawEvent['wikiCfpId']=cfpId
        rawEvent['deleted']=False
        scrape=WebScrape(debug=self.debug,timeout=self.timeout)
        triples=scrape.parseRDFa(url)
        if scrape.err:
            raise Exception(f"fromUrl {url} failed {scrape.err}")
        if self.crawlType==CrawlType.EVENT:
            self.rawEventFromWebScrape(rawEvent, triples, scrape)
        else:
            self.rawEventSeriesFromWebScrape(rawEvent,scrape)
        return rawEvent
    
__version__ = 0.3
__date__ = '2020-06-22'
__updated__ = '2021-07-31'    

DEBUG = 1

    
def main(argv=None): # IGNORE:C0111
    '''main program.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)    
        
    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    user_name="Wolfgang Fahl"
    program_license = '''%s

  Created by %s on %s.
  Copyright 2020-2021 TIB Hannover, Wolfgang Fahl. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc,user_name, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-d", "--debug", dest="debug", action="count", help="set debug level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument('--startId', type=int, help='eventId to start crawling from', required=True)
        parser.add_argument('--stopId', type=int, help='eventId to stop crawling at', required=True)
        parser.add_argument('--crawlType',type=str,default="Event",help="The crawlType - Event or Series")
        parser.add_argument('-p','--targetPath',type=str,help="targetPath (JSON directory) for crawl results")
        parser.add_argument('-t','--threads', type=int, help='number of threads to start', default=10)

        # Process arguments
        args = parser.parse_args()
        wikiCfpScrape=WikiCfpScrape(jsondir=args.targetPath,debug=args.debug)
        crawlBatch=CrawlBatch(args.threads, args.startId, args.stopId,args.crawlType,None)
        wikiCfpScrape.threadedCrawl(crawlBatch)
        
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 1
    except Exception as e:
        if DEBUG:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2     
    
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(main())
