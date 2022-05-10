from corpus.eventseriescompletion import EventSeriesCompletion
from tests.basetest import BaseTest
import json
from os import path
from ptp.ordinal import Ordinal

class TestEventSeriesCompletion(BaseTest):
    """
    tests EventSeriesCompletion
    """
    
    def getSeriesLod(self,seriesAcronym:str):
        '''
        get a list of dicts for a series for some test cases
        '''
        home = path.expanduser("~")
        cachedir= f"{home}/.conferencecorpus/esctestdata"
        with open(f'{cachedir}/{seriesAcronym}.json') as json_file:
            seriesData = json.load(json_file)
            return seriesData
        
    def testParseOrdinal(self):
        '''
        check the parsing of ordinals
        '''
        title='12th IEEE International Symposium on Wearable Computers (ISWC 2008), September 28 - October 1, 2008, Pittsburgh, PA, USA'
        item="irrelevant"
        pol=Ordinal.parseOrdinals(title, item)
        debug=self.debug
        #debug=True
        if (debug):
            print(pol)
        self.assertEqual([12],pol)
        
    def testGuessOrdinal(self):
        '''
        test guessing the ordinal
        '''
        debug=self.debug
        debug=True
        seriesIds=["VLDB"]
        for seriesId in seriesIds:
            seriesLod=self.getSeriesLod(seriesId)
            for event in seriesLod:
                Ordinal.addParsedOrdinal(event)
            if debug:
                print(f"Series {seriesId} (sorted)")        
            seriesLodByOrdinal=sorted(seriesLod,key=lambda event:event["ordinal"] if event.get("ordinal") in event else 0)
            for event in seriesLodByOrdinal:
                if debug:
                    print(f"""{event.get("ordinal","?")}:{event.get("year","?")}-{event["source"]}{event}""")
                
       
    def testMergingSeries(self):
        '''
        test merging event series from different sources
        '''
        vldbSeriesLod=self.getSeriesLod("VLDB")
        debug=self.debug
        #debug=True
        if debug:
            #print (vldbSeriesLod)
            print (len(vldbSeriesLod))
            
        vldbSeriesLod=sorted(vldbSeriesLod,key=lambda event:event["year"] if event.get("year") in event else 0)
        for vldbEvent in vldbSeriesLod:
            if vldbEvent["year"] is  not None:
                print(f"""{vldbEvent["year"]}:{vldbEvent["source"]}""")

    def test_getCompletedBlankSeries(self):
        """
        tests getCompletedBlankSeries
        extraction and completion of an event series for ordinal and year pairs
        """
        vldbSeriesLod = self.getSeriesLod("VLDB")
        completedBlankSeries = EventSeriesCompletion.getCompletedBlankSeries(vldbSeriesLod)
        # vldbSeriesLod has multiple records with same year but different ordinal → expect None
        self.assertEqual([], completedBlankSeries)
        seriesLod = self.getSeriesLod("3DUI")
        completedBlankSeries = EventSeriesCompletion.getCompletedBlankSeries(seriesLod)
        self.assertEqual(12, len(completedBlankSeries))
        self.assertEqual((2006,1), completedBlankSeries[0])
        self.assertEqual((2017,12), completedBlankSeries[-1])

    def test_getFrequency(self):
        """
        tests getFrequency
        """
        self.assertEqual(1,EventSeriesCompletion.getFrequency([(2000, 1), (2001, 2), (2002,3)]))
        self.assertEqual(2, EventSeriesCompletion.getFrequency([(2000, 1), (2002, 2), (2004, 3)]))
        self.assertEqual(0, EventSeriesCompletion.getFrequency([(2000, 1), (2001, 2), (2004, 3)]))
        self.assertEqual(0, EventSeriesCompletion.getFrequency([(2000, 1)]))
        self.assertEqual(0, EventSeriesCompletion.getFrequency([(2000, 1), (2001, 5), (2002, 3)]))
        self.assertEqual(0, EventSeriesCompletion.getFrequency([(2000, 1), (2002, 2), (2004, 3), (2005,4), (2006, 5)]))
        self.assertEqual(0, EventSeriesCompletion.getFrequency([(2011, 2), (2013, 2), (2015, 4), (2016, 5), (2017, 6), (2018, 7), (2019, 8), (2020, 9), (2021, 10)]))
