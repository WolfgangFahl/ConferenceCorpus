'''
Created on 2021-08-20

@author: wf
'''
import unittest
from geopy.geocoders import Nominatim
from OSMPythonTools.nominatim import Nominatim as ONominatim
import json
class TestGeopy(unittest.TestCase):
    '''
    test geopy and other nominatim handlers
    '''


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testNominatim(self):
        '''
        test nominatim results - especially the extra tags
        '''
        geolocator = Nominatim(user_agent="ConferenceCorpus")
        nominatim = ONominatim(cacheDir="/tmp")
        show=self.debug
        for example in ["London","Dublin","Vienna Austra","Athens, Georgia","St. Petersburg","Arlington, VA"]:
            location = geolocator.geocode(example)
            if show:
                print(example)
            if location is not None:
                if show:
                    print(location)
            nresult=nominatim.query(example,params={"extratags":"1"})
            for result in nresult._json:
                if show:
                    print(json.dumps(result,indent=4))
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()