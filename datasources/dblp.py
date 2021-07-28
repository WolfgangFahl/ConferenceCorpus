'''
Created on 2021-07-28

@author: th
'''
from corpus.event import EventSeriesManager,EventSeries, Event, EventManager
from lodstorage.storageconfig import StorageConfig
from datasources.dblpxml import Dblp


class DblpEventSeries(EventSeries):
    pass


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


    def fromDblp(self, dblp:Dblp):
        '''

        Args:
            dblp(Dblp): xml dump access code

        '''
        self.sqlDb=dblp.getXmlSqlDB()
        query = """select conf,count(*) as count,min(year) as minYear,max(year) as maxYear
        from proceedings 
        where conf is not null
        group by conf
        order by 2 desc"""
        listOfDicts = self.sqlDb.query(query)
        for record in listOfDicts:
            es = DblpEventSeries()
            es.fromDict(record)
            self.getList().append(es)
