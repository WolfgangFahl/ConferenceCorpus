'''
Created on 2021-07-28

@author: th
'''
from corpus.event import EventSeriesManager,EventSeries, Event, EventManager
from lodstorage.storageconfig import StorageConfig
from datasources.dblpxml import Dblp

class DblpEvent(Event):
    
    pass


class DblpEventSeries(EventSeries):
    pass

class DblpEventManager(EventManager):
    '''
    dblp event access (in fact proceedings)
    
    Example event: https://dblp.org/db/conf/aaai/aaai2020.html
    
    '''
    def __init__(self, dblp:Dblp,config: StorageConfig = None):
        '''
        Constructor
        '''
        super(DblpEventManager, self).__init__(name="Dblp", clazz=DblpEventSeries,
                                                         tableName="dblp_eventseries", config=config)
        self.dblp=dblp
        self.sqlDb=self.dblp.getXmlSqlDB()
    pass

    def getLoDfromDblp(self)->list:
        '''
        get the LoD for the event series
            
        Return:
            list: the list of dict with my series data

        '''
        query = """select conf as acronym,title,year,url,series
        from proceedings 
        order by acronym,year"""
        listOfDicts = self.sqlDb.query(query)
        return listOfDicts

class DblpEventSeriesManager(EventSeriesManager):
    '''
    dblp event series access
    Example event series: https://dblp.org/db/conf/aaai/index.html

    dblp provides regular dblp xml dumps
    '''

    def __init__(self, dblp:Dblp,config: StorageConfig = None):
        '''
        Constructor
        '''
        super(DblpEventSeriesManager, self).__init__(name="Dblp", clazz=DblpEventSeries,
                                                         tableName="dblp_eventseries", config=config)
        self.dblp=dblp
        self.sqlDb=self.dblp.getXmlSqlDB()

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
        return listOfDicts
