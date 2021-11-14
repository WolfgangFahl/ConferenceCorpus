'''
Created on 2021-07-28

@author: th
'''
from corpus.event import EventSeriesManager, EventSeries, Event, EventManager
from lodstorage.storageconfig import StorageConfig
from corpus.datasources.dblpxml import DblpXml
from corpus.eventcorpus import EventDataSource, EventDataSourceConfig
import re
from datetime import datetime

class Dblp(EventDataSource):
    '''
    scientific events from https://dblp.org
    '''
    sourceConfig = EventDataSourceConfig(lookupId="dblp", name="dblp", url='https://dblp.org/', title='dblp computer science bibliography', tableSuffix="dblp")
    
    def __init__(self):
        '''
        constructor
        '''
        super().__init__(DblpEventManager(), DblpEventSeriesManager(), Dblp.sourceConfig)
        self.dayPattern=r""
        delim=""
        for day in range(1,31):
            self.dayPattern=self.dayPattern+f"{delim}{day}"
            delim="|"
        self.monthPattern=r"January|February|March|April|May|June|July|August|September|October|November|December"
        self.yearPattern=r"([12][0-9]{3})"
        self.ws=r"\s+"
        self.dateRangePattern=f"^({self.dayPattern})[-]({self.dayPattern}){self.ws}({self.monthPattern}){self.ws}({self.yearPattern})$"
        
    def strToDate(self,dateStr):
        '''
        Args:
            dateStr(str): the string to convert
            
        Return:
            datetime: the date
        '''
        d=None
        try:
            d = datetime.strptime(dateStr, '%d %B %Y')
        except ValueError as _ve:
            
            pass
        return d
        

    def getDateRange(self,dateStr):
        '''
        given a dblp date string create a date range
        
        Args:
            dateStr(str): the date string to analyze
            
        Returns:
            dict: containing year, startDate, endDate
        examples:
            18-21 September 2005

        '''
        result={}
        if dateStr is not None:
            yearOnly=re.search(f"^{self.yearPattern}$",dateStr)
            dateRangeMatch=re.search(self.dateRangePattern,dateStr)
            if yearOnly: 
                result['year']=int(yearOnly.group(1))
            elif dateRangeMatch:      
                fromDay=dateRangeMatch.group(1)
                toDay=dateRangeMatch.group(2)
                month=dateRangeMatch.group(3)
                year=dateRangeMatch.group(4)
                startDateStr=f"{fromDay} {month} {year}"
                toDateStr=f"{toDay} {month} {year}"          
                result['startDate']=self.strToDate(startDateStr)
                result['endDate']=self.strToDate(toDateStr)
        if 'startDate' in result:
                result['year']=result['startDate'].year
        return result

        
class DblpEvent(Event):
    '''
    a Dblp Event
    
    Example event: https://dblp.org/db/conf/aaai/aaai2020.html
    '''

    def __init__(self):
        '''constructor '''
        super().__init__()
        pass
        
    
    @staticmethod
    def postProcessLodRecord(rawEvent:dict):
        '''
        fix the given raw Event
        
        Args:
            rawEvent(dict): the raw event record to fix
        '''
        if 'url' in rawEvent:
            rawEvent["url"] = f"https://dblp.org/{rawEvent['url']}" 
        if "year" in rawEvent:
            # set year to integer value
            yearStr = rawEvent['year']
            year = None
            try:
                year = int(yearStr)
            except Exception as _ne:
                pass
            rawEvent['year'] = year
            # if there is a booktitle create acronym
            if "booktitle" in rawEvent:
                booktitle = rawEvent['booktitle']
                if booktitle is not None and year is not None:
                    acronym = f"{booktitle} {year}"
                    rawEvent["acronym"] = acronym 
        doiprefix = "https://doi.org/"
        if 'ee' in rawEvent:
            ees = rawEvent['ee']
            if ees:
                for ee in ees.split(","):
                    if ee.startswith(doiprefix):
                        doi = ee.replace(doiprefix, "")
                        rawEvent["doi"] = doi 


class DblpEventSeries(EventSeries):
    '''
    a Dblp Event Series
    
    Example event series: https://dblp.org/db/conf/aaai/index.html
    '''

    def __init__(self):
        '''constructor '''
        super().__init__()
        pass
        

class DblpEventManager(EventManager):
    '''
    dblp event access (in fact proceedings)
    
    Example event: https://dblp.org/db/conf/aaai/aaai2020.html
    
    '''
    cacheOnly=False

    def __init__(self, config: StorageConfig=None):
        '''
        Constructor
        '''
        super(DblpEventManager, self).__init__(name="DblpEvents", sourceConfig=Dblp.sourceConfig, clazz=DblpEvent, config=config)

    pass

    def configure(self):
        '''
        configure me
        '''
        withProgress = False
        if DblpEventManager.cacheOnly:
            return
        if not hasattr(self, "dblpXml"): 
            self.dblpXml = DblpXml()
            self.dblpXml.warnFullSize()
            withProgress = True
        self.sqlDb = self.dblpXml.getXmlSqlDB(showProgress=withProgress)
        if not hasattr(self, "getListOfDicts"):
            self.getListOfDicts = self.getLoDfromDblp

    def getLoDfromDblp(self) -> list:
        '''
        get the LoD for the event series
            
        Return:
            list: the list of dict with my series data

        '''
        query = """select conf as series,title,year,url,booktitle,series as publicationSeries,ee,isbn,mdate,key as eventId
        from proceedings 
        order by series,year"""
        listOfDicts = self.sqlDb.query(query)
        self.setAllAttr(listOfDicts, "source", "dblp")
        self.postProcessLodRecords(listOfDicts)
        return listOfDicts


class DblpEventSeriesManager(EventSeriesManager):
    '''
    dblp event series access
    Example event series: https://dblp.org/db/conf/aaai/index.html

    dblp provides regular dblp xml dumps
    '''

    def __init__(self, config: StorageConfig=None):
        '''
        Constructor
        '''
        super().__init__(name="DblpEventSeries", sourceConfig=Dblp.sourceConfig, clazz=DblpEventSeries, config=config)
        
    def configure(self):
        '''
        configure me
        '''
        withProgress = False
        if DblpEventManager.cacheOnly:
            return
        if not hasattr(self, "dblpXml"): 
            self.dblpXml = DblpXml()
            self.dblpXml.warnFullSize()
            withProgress = True
        self.sqlDb = self.dblpXml.getXmlSqlDB(showProgress=withProgress)
        if not hasattr(self, "getListOfDicts"):
            self.getListOfDicts = self.getLoDfromDblp

    def getLoDfromDblp(self) -> list:
        '''

        get the list of dicts for the event data
            
        Return:
            list: the list of dict with my event data

        '''
        query = """select conf as acronym,conf as eventSeriesId,count(*) as count,min(year) as minYear,max(year) as maxYear
        from proceedings 
        where acronym is not null
        group by acronym
        order by 2 desc"""
        listOfDicts = self.sqlDb.query(query)
        self.setAllAttr(listOfDicts, "source", "dblp")
        self.postProcessLodRecords(listOfDicts)
        return listOfDicts
