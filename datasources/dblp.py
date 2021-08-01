'''
Created on 2021-07-28

@author: th
'''
from corpus.event import EventSeriesManager,EventSeries, Event, EventManager
from lodstorage.storageconfig import StorageConfig
from datasources.dblpxml import Dblp

class DblpEvent(Event):
    '''
    a Dblp Event
    
    Example event: https://dblp.org/db/conf/aaai/aaai2020.html
    '''
    def __init__(self):
        '''constructor '''
        super().__init__()
        pass


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
    def __init__(self, config: StorageConfig = None):
        '''
        Constructor
        '''
        super(DblpEventManager, self).__init__(name="DblpEvents", clazz=DblpEventSeries,
                                                         tableName="dblp_eventseries", config=config)
    pass

    def configure(self):
        '''
        configure me
        '''
        if not hasattr(self, "dblp"): 
            self.dblp=Dblp()
            self.dblp.warnFullSize()
        self.sqlDb=self.dblp.getXmlSqlDB()
        if not hasattr(self,"getListOfDicts"):
            self.getListOfDicts=self.getLoDfromDblp

    def getLoDfromDblp(self)->list:
        '''
        get the LoD for the event series
            
        Return:
            list: the list of dict with my series data

        '''
        query = """select conf as series,title,year,url,series as publicationSeries
        from proceedings 
        order by series,year"""
        listOfDicts = self.sqlDb.query(query)
        self.setAllAttr(listOfDicts,"source","dblp")
        return listOfDicts

class DblpEventSeriesManager(EventSeriesManager):
    '''
    dblp event series access
    Example event series: https://dblp.org/db/conf/aaai/index.html

    dblp provides regular dblp xml dumps
    '''

    def __init__(self, config: StorageConfig = None):
        '''
        Constructor
        '''
        super(DblpEventSeriesManager, self).__init__(name="DblpEventSeries", clazz=DblpEventSeries,
                                                         tableName="dblp_eventseries", config=config)
        
    def configure(self):
        '''
        configure me
        '''
        if not hasattr(self, "dblp"):  
            self.dblp=Dblp()
            self.dblp.warnFullSize()
        self.sqlDb=self.dblp.getXmlSqlDB()
        if not hasattr(self,"getListOfDicts"):
            self.getListOfDicts=self.getLoDfromDblp

    def getLoDfromDblp(self)->list:
        '''

        get the list of dicts for the event data
            
        Return:
            list: the list of dict with my event data

        '''
        query = """select conf as acronym,count(*) as count,min(year) as minYear,max(year) as maxYear
        from proceedings 
        where acronym is not null
        group by acronym
        order by 2 desc"""
        listOfDicts = self.sqlDb.query(query)
        self.setAllAttr(listOfDicts,"source","dblp")
        return listOfDicts
