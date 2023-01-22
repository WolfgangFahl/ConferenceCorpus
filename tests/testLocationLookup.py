'''
Created on 2023-01-22

@author: wf
'''
import json
from corpus.locationfixer import LocationLookup
from tests.basetest import BaseTest

class TestLocatioLookup(BaseTest):
    '''
    test Location Lookup
    '''

    def testPredefinedLocations(self):
        """
        test the predefined Locations hash table
        """
        LocationLookup.initPredefinedLocations()
        count=len(LocationLookup.predefinedLocations)
        debug=self.debug
        debug=True
        if debug:
            print(json.dumps(LocationLookup.predefinedLocations,indent=2))
            print(f"{count} predefinedLocation Terms added")
     