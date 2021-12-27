'''
Created on 2021-08-20

@author: wf
'''
import unittest
from tests.datasourcetoolbox import DataSourceTest
from corpus.nominatim import NominatimWrapper
class TestGeopy(DataSourceTest):
    '''
    test geopy and other nominatim handlers
    '''

    def testNominatim(self):
        '''
        test nominatim results - especially the extra tags
        '''
        examples=[{
            "city":"London",
            "q": "Q84",
            "expected": "England"
        },{
            "city":"Dublin",
            "q": "Q1761",
            "expected": "Éire"
        },{
            "city":"Vienna Austria",
            "q": "Q1741",
            "expected": "Österreich"
        },{
            "city":"Athens, Georgia",
            "q": "Q203263",
            "expected": "Athens-Clarke County"
        },{
            "city":"St. Petersburg",
            "q": "Q49236",
            # not really expected but that's the state of affairs 2021-12-27
            "expected": "Florida"
        },
        {
            # so for St. Petersburg we need to be more specific
            "city":"St. Petersburg, Russia",
            "q": "Q656",
            # to get the russian one
            "expected": "Санкт-Петербург"
        },{
            "city":"Arlington, VA",
            # not really satisfactory but that's the state of affairs 2021-12-27
            "q": None,
            "expected": "Virginia"
        }
        ]
        
        nw=NominatimWrapper()
        show=self.debug
        show=True
        for example in examples:
            city=example["city"]
            location = nw.geolocator.geocode(city)
            wikidataId=nw.lookupWikiDataId(city)
            q=example["q"]
            expected=example["expected"] 
            if show:
                print(f"{city:<22}:{str(wikidataId):<7}/{str(q):<7}:{location}→{expected}")
            self.assertEqual(str(q),str(wikidataId))
            self.assertTrue(expected in str(location))
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()