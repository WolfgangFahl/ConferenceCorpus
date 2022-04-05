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
            seriesLodByOrdinal=sorted(seriesLod,key=lambda event:event["ordinal"] if "ordinal" in event else 0) 
            for event in seriesLodByOrdinal:
                if debug:
                    print(f"""{event.get("ordinal","?")}:{event.get("year","?")}-{event["source"]}{event}""")
                
       
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
        
        