'''
Created on 2021-07-39

@author: wf
'''
from corpus.eventcorpus import EventCorpus, EventDataSource
from datasources.dblp import DblpEventManager,DblpEventSeriesManager
from datasources.wikidata import WikidataEventManager,WikidataEventSeriesManager
from datasources.openresearch import OREventManager,OREventSeriesManager

class CorpusLookup(object):
    '''
    search and lookup for different EventCorpora
    '''

    def __init__(self,configure:callable=None):
        '''
        Constructor
        
        Args:
            configure(callable): Callback to configure the corpus lookup
        '''
        self.configure=configure
        self.eventCorpus=EventCorpus()
        self.eventCorpus.addDataSource(DblpEventManager(),DblpEventSeriesManager(),name="dblp",url='https://dblp.org/',title='dblp computer science bibliography')
        self.eventCorpus.addDataSource(WikidataEventManager(),WikidataEventSeriesManager(),name="wikidata",url='https://www.wikidata.org/wiki/Wikidata:Main_Page',title='Wikidata')
        self.eventCorpus.addDataSource(OREventManager(),OREventSeriesManager(),name="or",url='https://www.openresearch.org/wiki/Main_Page',title='OPENRESEARCH')
        self.eventCorpus.addDataSource(OREventManager(),OREventSeriesManager(),name="or-backup",url='https://www.openresearch.org/wiki/Main_Page',title='OPENRESEARCH')
        self.eventCorpus.addDataSource(OREventManager(),OREventSeriesManager(),name="orclone",url='https://confident.dbis.rwth-aachen.de/or/index.php?title=Main_Page',title='OPENRESEARCH-clone')
        self.eventCorpus.addDataSource(OREventManager(),OREventSeriesManager(),name="orclone-backup",url='https://confident.dbis.rwth-aachen.de/or/index.php?title=Main_Page',title='OPENRESEARCH-clone')
        
    def getDataSource(self,dataSourceName:str)->EventDataSource:
        '''
        get the given data source
        
        Args:
            dataSourceName(str): the name of the data source to get
            
        Return:
            EventDataSource: the data source

        '''
        eventDataSource=None
        if dataSourceName in self.eventCorpus.eventDataSources:
            eventDataSource=self.eventCorpus.eventDataSources[dataSourceName]
        return eventDataSource
        
    def load(self):
        '''
        load the event corpora
        '''
        if self.configure:
            self.configure(self)
        self.eventCorpus.loadAll()