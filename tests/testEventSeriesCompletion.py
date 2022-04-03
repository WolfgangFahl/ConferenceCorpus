from tests.basetest import BaseTest
import json
from os import path
from corpus.eventseriescompletion import EventSeriesCompletion

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
        
    def testGuessOrdinal(self):
        '''
        test guessing the ordinal
        '''
        vldbSeriesLod=self.getSeriesLod("VLDB")
        for vldbEvent in vldbSeriesLod:
            pol=EventSeriesCompletion.guessOrdinal(vldbEvent)
            if len(pol)>0:
                print(pol,vldbEvent)

    def testMergingSeries(self):
        '''
        '''
        vldbSeriesLod=self.getSeriesLod("VLDB")
        print (vldbSeriesLod)
        print (len(vldbSeriesLod))
        for vldbEvent in vldbSeriesLod:
            if vldbEvent["ordinal"] is  not None:
                print(f"""{vldbEvent["ordinal"]}""")
        
        