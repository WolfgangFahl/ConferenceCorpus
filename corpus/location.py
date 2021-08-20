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
        "Virtual Event USA": "Q30",
        "Virtual USA": "Q30",
        "London United Kingdom": "Q84",
        "Brno":"Q14960",
        "Cancun":"Q8969",
        "St. Petersburg": "Q656",
        "Gothenburg Sweden": "Q25287",
        "Los Angeles California": "Q65",
        "Zurich, Switzerland": "Q72",
        "Barcelona Spain": "Q1492",
        "Vienna Austria": "Q1741",
        "Seoul Republic of Korea": "Q8684",
        "Seattle WA USA": "Q5083",
        "Singapore Singapore":"Q334",
        "Tokyo Japan": "Q1490",
        "Vancouver BC Canada": "Q24639",
        "Vancouver British Columbia Canada": "Q24639",
        "Amsterdam Netherlands":"Q727",
        "Paris France": "Q90",
        "Nagoya": "Q11751",
        "Marrakech":"Q101625",
        "Austin Texas":"Q16559",
        "Chicago IL USA":"Q1297",
        "Bangkok Thailand":"Q1861",
        "Firenze, Italy":"Q2044",
        "Florence Italy":"Q2044",
        "Timisoara":"Q83404",
        "Langkawi":"Q273303",
        "Beijing China":"Q956",
        "Berlin Germany": "Q64",
        "Prague Czech Republic":"Q1085",
        "Portland Oregon USA":"Q6106",
        "Portland OR USA":"Q6106",
        "Pittsburgh PA USA":"Q1342",
        "Новосибирск":"Q883",
        "Los Angeles CA USA":"Q65",
        "Kyoto Japan": "Q34600"
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
        