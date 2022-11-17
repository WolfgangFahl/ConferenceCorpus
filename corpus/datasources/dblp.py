'''
Created on 2021-07-28

@author: th
'''
from corpus.event import EventSeriesManager, EventSeries, Event, EventManager
from lodstorage.storageconfig import StorageConfig
from corpus.datasources.dblpxml import DblpXml
from corpus.eventcorpus import EventDataSource, EventDataSourceConfig
from ptp.ordinal import Ordinal
import re
from datetime import datetime

class Dblp(EventDataSource):
    '''
    scientific events from https://dblp.org
    '''
    sourceConfig = EventDataSourceConfig(lookupId="dblp", name="dblp", url='https://dblp.org/', title='dblp computer science bibliography', tableSuffix="dblp",locationAttribute="location")
    
    def __init__(self):
        '''
        constructor
        '''
        super().__init__(DblpEventManager(), DblpEventSeriesManager(), Dblp.sourceConfig)
       
    @classmethod
    def setPatterns(cls):
        if hasattr(cls,"dayPattern"):
            return
        cls.dayPattern=r""
        cls.dayPatternWithSuffix=r""
        delim=""
        for day in range(1,31):
            # https://stackoverflow.com/a/739266/1497139
            cls.dayPattern=cls.dayPattern+f"{delim}{day}"
            delim="|"
        cls.monthPattern=r"January|February|March|April|May|June|July|August|September|October|November|December"
        cls.yearPattern=r"([12][0-9]{3})"
        cls.ws=r"\s+"
        cls.dateRangePattern=f"^\s*({cls.dayPattern})[-]({cls.dayPattern})(st|nd|rd|th)?{cls.ws}({cls.monthPattern}){cls.ws}({cls.yearPattern})\s*[.]?$"        


    @classmethod
    def strToDate(cls,dateStr):
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
    
    @classmethod
    def getDateRangeFromTitle(cls,title:str):
        dateRange={}
        if title is not None:
            parts=title.split(",")
            datePartStr=parts[len(parts)-1]
            dateRange=Dblp.getDateRange(datePartStr)
        return dateRange 
    
    @classmethod
    def getDateRange(cls,dateStr):
        '''
        given a dblp date string create a date range
        
        Args:
            dateStr(str): the date string to analyze
            
        Returns:
            dict: containing year, startDate, endDate
        jpexamples:
            18-21 September 2005

        '''
        cls.setPatterns()
        result={}
        if dateStr is not None:
            yearOnly=re.search(f"^{cls.yearPattern}$",dateStr)
            dateRangeMatch=re.search(cls.dateRangePattern,dateStr)
            if yearOnly: 
                result['year']=int(yearOnly.group(1))
            elif dateRangeMatch:      
                fromDay=dateRangeMatch.group(1)
                toDay=dateRangeMatch.group(2)
                month=dateRangeMatch.group(4)
                year=dateRangeMatch.group(5)
                startDateStr=f"{fromDay} {month} {year}"
                toDateStr=f"{toDay} {month} {year}"   
                startDate=cls.strToDate(startDateStr)   
                endDate=cls.strToDate(toDateStr)
                if startDate and endDate: 
                    result['startDate']=startDate
                    result['endDate']=endDate
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
        if 'title' in rawEvent:   
            title=rawEvent["title"]
            dateRange=Dblp.getDateRangeFromTitle(title)
            for key, value in dateRange.items():
                rawEvent[key]=value
            Ordinal.addParsedOrdinal(rawEvent)
                
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
    
    def addLocations(self):
        # extract locations
        for dblpEvent in self.events:
            title=dblpEvent.title
            if title is not None:
                parts=title.split(",")
                if len(parts)>3:
                    dblpEvent.location=f"{parts[2].strip()}, {parts[3].strip()}"

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

