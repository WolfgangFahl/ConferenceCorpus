'''
Created on 2021-07-39

@author: wf
'''
from corpus.eventcorpus import EventCorpus
from datasources.dblp import DblpEventManager,DblpEventSeriesManager
from datasources.wikidata import WikidataEventManager,WikidataEventSeriesManager

class CorpusLookup(object):
    '''
    search and lookup for different EventCorpora
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.eventCorpus=EventCorpus()
        self.eventCorpus.addDataSource(DblpEventManager(),DblpEventSeriesManager(),name="dblp",url='https://dblp.org/',title='dblp computer science bibliography')
        self.eventCorpus.addDataSource(WikidataEventManager(),WikidataEventSeriesManager(),name="wikidata",url='https://www.wikidata.org/wiki/Wikidata:Main_Page',title='Wikidata')
        
    def load(self):
        '''
        load the event corpora
        '''
        self.eventCorpus.loadAll()