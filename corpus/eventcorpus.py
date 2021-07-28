'''
Created on 2021-04-16

@author: wf
'''

from wikifile.wikiFileManager import WikiFileManager
from os.path import expanduser
import os
from lodstorage.csv import CSV
from lodstorage.lod import LOD

from corpus.event import EventManager, EventSeriesManager


class EventCorpus(object):
    '''
    Towards a gold standard event corpus  and observatory ...
    '''

    def __init__(self,debug=False,verbose=False):
        '''
        Constructor
        '''
        self.debug=debug
        self.verbose=verbose
        self.eventManagers={}

    def addManagers(self, eventManager:EventManager, eventSeriesManager:EventSeriesManager):
        '''
        adds the given managers to the eventManagers of this EventCorpus
        Args:
            eventManager(EventManager):
            eventSeriesManager(EventSeriesManager):
        '''
        pass

    def getEventsInSeries(self,seriesAcronym):
        """
        Return all the events in a given series.
        """
        if seriesAcronym in self.seriesAcronymLookup:
            seriesEvents = self.seriesLookup[seriesAcronym]
            if self.debug:
                print(f"{seriesAcronym}:{len(seriesEvents):4d}")
        else:
            if self.debug:
                print(f"Event Series Acronym {seriesAcronym} lookup failed")
            return None
        return seriesEvents
