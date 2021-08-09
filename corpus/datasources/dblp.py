'''
Created on 2021-07-28

@author: th
'''
from corpus.event import EventSeriesManager, EventSeries, Event, EventManager
from lodstorage.storageconfig import StorageConfig
from corpus.datasources.dblpxml import DblpXml
from corpus.eventcorpus import EventDataSource, EventDataSourceConfig


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

        
class DblpEvent(Event):
    '''
    a Dblp Event
    
    Example event: https://dblp.org/db/conf/aaai/aaai2020.html
    '''

    def __init__(self):
        '''constructor '''
        super().__init__()
        pass
    
    def asWikiMarkup(self)->str:
        '''
        Return:
            my WikiMarkup
        '''
        markup=f"""{{{{Event
|Acronym={self.acronym}
|Title={self.title}
|Series={self.series}
}}}}"""
#|Type=Symposium
#|Start date=2020/03/22
#|End date=2020/03/26
#|Submission deadline=2019/09/03
#|Homepage=http://ieeevr.org/2020/
#|City=Atlanta
#|Country=USA
#}}
        return markup
       
        
    
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
    
    def asWikiMarkup(self):
        '''
        copy me to the given wiki
        
        see https://github.com/WolfgangFahl/ConferenceCorpus/issues/10
        '''
        markup=f"""{{{{Event series
|Acronym=
|Title=
|DblpSeries={self.acronym}
}}}}"""
        #|WikiDataId=Q105456162
        return markup
        

class DblpEventManager(EventManager):
    '''
    dblp event access (in fact proceedings)
    
    Example event: https://dblp.org/db/conf/aaai/aaai2020.html
    
    '''

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
