'''
Created on 2021-08-11

@author: wf
'''
#from lodstorage.entity import EntityManager
from geograpy.locator import LocationContext

class LocationLookup:
    '''
    lookup locations
    '''
    preDefinedLocations={
        "Not Known": None,
        "Online": None,
        "Washington, DC, USA": "Q61",
        "Bangalore": "Q1355",
        "Bangalore, India": "Q1355",
        "Xi'an": "Q5826",
        "Xi'an, China": "Q5826",
        "Virtual Event USA": None,
        "London United Kingdom": "Q84",
        "Brno":"Q14960",
        "Cancun":"Q8969",
        "St. Petersburg": "Q656",
        "Gothenburg Sweden": "Q25287",
        "Los Angeles California": "Q65",
        "Zurich, Switzerland": "Q72",
        "Barcelona Spain": "Q1492",
    }

    def __init__(self):
        '''
        Constructor
        '''
        self.locationContext=LocationContext.fromCache()
        
    def lookup(self,locationText:str):
        '''
        lookup the given location by the given locationText
        '''
        if locationText in LocationLookup.preDefinedLocations:
            locationId=LocationLookup.preDefinedLocations[locationText]
            if locationId is None:
                return None
            else:
                location=self.locationContext._cityLookup[locationId]
                return location
        locations=self.locationContext.locateLocation(locationText)
        if len(locations)>0:
            return locations[0]
        else:
            return None
        