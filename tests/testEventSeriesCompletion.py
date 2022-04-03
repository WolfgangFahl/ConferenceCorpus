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
        debug=self.debug
        debug=True
        vldbSeriesLod=self.getSeriesLod("VLDB")
        for vldbEvent in vldbSeriesLod:
            pol=EventSeriesCompletion.guessOrdinal(vldbEvent)
            if len(pol)>0:
                if debug:
                    print(pol,vldbEvent)

    def testMergingSeries(self):
        '''
        test merging event series from different sources
        '''
        vldbSeriesLod=self.getSeriesLod("VLDB")
        debug=self.debug
        debug=True
        if debug:
            #print (vldbSeriesLod)
            print (len(vldbSeriesLod))
            
        vldbSeriesLod=sorted(vldbSeriesLod,key=lambda event:event["year"])
        for vldbEvent in vldbSeriesLod:
            if vldbEvent["year"] is  not None:
                print(f"""{vldbEvent["year"]}:{vldbEvent["source"]}""")
        
        