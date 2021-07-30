'''
Created on 2021-07-39

@author: wf
'''
from corpus.eventcorpus import EventCorpus, EventDataSource
from corpus.event import EventStorage
from datasources.dblp import DblpEventManager,DblpEventSeriesManager
from datasources.wikidata import WikidataEventManager,WikidataEventSeriesManager
from datasources.openresearch import OREventManager,OREventSeriesManager

class CorpusLookup(object):
    '''
    search and lookup for different EventCorpora
    '''

    def __init__(self,configure:callable=None,debug=False):
        '''
        Constructor
        
        Args:
            configure(callable): Callback to configure the corpus lookup
        '''
        self.debug=debug
        self.configure=configure
        self.eventCorpus=EventCorpus()
        self.eventCorpus.addDataSource(DblpEventManager(),DblpEventSeriesManager(),lookupId="dblp",name="dblp",url='https://dblp.org/',title='dblp computer science bibliography',tablePrefix="dblp")
        self.eventCorpus.addDataSource(WikidataEventManager(),WikidataEventSeriesManager(),lookupId="wikidata",name="Wikidata",url='https://www.wikidata.org/wiki/Wikidata:Main_Page',title='Wikidata',tablePrefix="wikidata")
        self.eventCorpus.addDataSource(OREventManager(),OREventSeriesManager(),lookupId="or",name="OR_Triples",url='https://www.openresearch.org/wiki/Main_Page',title='OPENRESEARCH-api',tablePrefix="orapi")
        self.eventCorpus.addDataSource(OREventManager(),OREventSeriesManager(),lookupId="or-backup",name="OR_Markup",url='https://www.openresearch.org/wiki/Main_Page',title='OPENRESEARCH-wiki',tablePrefix="orwiki")
        self.eventCorpus.addDataSource(OREventManager(),OREventSeriesManager(),lookupId="orclone",name="OR_Clone_Triples",url='https://confident.dbis.rwth-aachen.de/or/index.php?title=Main_Page',title='OPENRESEARCH-clone-api',tablePrefix="orcapi")
        self.eventCorpus.addDataSource(OREventManager(),OREventSeriesManager(),lookupId="orclone-backup",name="OR_Clone_Markup",url='https://confident.dbis.rwth-aachen.de/or/index.php?title=Main_Page',title='OPENRESEARCH-clone-wiki',tablePrefix="orcwiki")
        
    def getDataSource(self,lookupId:str)->EventDataSource:
        '''
        get the given data source
        
        Args:
            lookupId(str): the lookupId of the data source to get
            
        Return:
            EventDataSource: the data source

        '''
        eventDataSource=None
        if lookupId in self.eventCorpus.eventDataSources:
            eventDataSource=self.eventCorpus.eventDataSources[lookupId]
        return eventDataSource
        
    def load(self):
        '''
        load the event corpora
        '''
        if self.configure:
            self.configure(self)
        self.eventCorpus.loadAll()