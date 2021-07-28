'''
Created on 2021-04-16

@author: wf
'''

from wikifile.wikiFileManager import WikiFileManager
from os.path import expanduser
import os
from lodstorage.csv import CSV
from lodstorage.lod import LOD

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


    def generateCSV(self,pageTitles,filename,filepath=None):
        """
        Generate a csv with the given pageTitles
        Args:
            pageTitles(list):List of pageTitles to generate CSV from
            filename(str):CSV file name
            filepath(str):filepath to create csv. Default: ~/.ptp/csvs/
        """
        if filepath is None:
            home=expanduser("~")
            filepath= f"{home}/.or/csvs"
        lod = self.wikiFileManager.exportWikiSonToLOD(pageTitles, 'Event')
        if self.debug:
            print(pageTitles)
            print(lod)

        savepath =f"{filepath}/{filename}.csv"
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        CSV.storeToCSVFile(lod, savepath,withPostfix=True)
        return savepath

    def getEventCsv(self,eventTitle):
        """
        Gives a csv file for the eventTitle
        """
        return self.generateCSV([eventTitle],eventTitle)

    def getEventSeriesCsv(self,eventSeriesTitle):
        """
        Gives a csv file for all the events the given eventSeriesTitle
        """
        eventsInSeries = self.getEventsInSeries(eventSeriesTitle)
        pageTitles = []
        for event in eventsInSeries:
            if hasattr(event, 'pageTitle'):
                pageTitles.append(event.pageTitle)
        return self.generateCSV(pageTitles,eventSeriesTitle)

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
