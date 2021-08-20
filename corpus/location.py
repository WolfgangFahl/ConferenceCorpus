'''
Created on 2021-08-11

@author: wf
'''
#from lodstorage.entity import EntityManager
from geograpy.locator import LocationContext
import OSMPythonTools
from OSMPythonTools.nominatim import Nominatim 
import os
import logging

class LocationLookup:
    '''
    lookup locations
    '''
    preDefinedLocations={
        "Not Known": None,
        "Online": None,
    }
    other={
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
        cacheRootDir=LocationContext.getDefaultConfig().cacheRootDir
        cacheDir=f"{cacheRootDir}/.nominatim"
        if not os.path.exists(cacheDir):
            os.makedirs(cacheDir)
            
        self.nominatim = Nominatim(cacheDir=cacheDir)
        logging.getLogger('OSMPythonTools').setLevel(logging.ERROR)
        
        
    def getCityByWikiDataId(self,wikidataID:str):
        '''
        get the city for the given wikidataID
        '''
        citiesGen=self.locationContext.cityManager.getLocationsByWikidataId(wikidataID)
        if citiesGen is not None:
            cities=list(citiesGen)
            if len(cities)>0:
                return cities[0]
        else:
            return None
        
    def lookupNominatim(self,locationText:str):
        location=None
        nresult=self.nominatim.query(locationText,params={"extratags":"1"})
        nlod=nresult._json
        if len(nlod)>0:
            nrecord=nlod[0]
            if "extratags" in nrecord:
                extratags=nrecord["extratags"]
                if "wikidata" in extratags:
                    wikidataID=extratags["wikidata"]
                    location=self.getCityByWikiDataId(wikidataID)
        return location
        
    def lookup(self,locationText:str):
        lg=self.lookupGeograpy(locationText)
        ln=self.lookupNominatim(locationText)
        if ln is not None and lg is not None and not ln.wikidataid==lg.wikidataid:
            print(f"❌{locationText}→{lg}!={ln}")
            return None
        return lg
        
    def lookupGeograpy(self,locationText:str):
        '''
        lookup the given location by the given locationText
        '''
        if locationText in LocationLookup.preDefinedLocations:
            locationId=LocationLookup.preDefinedLocations[locationText]
            if locationId is None:
                return None
            else:
                location=self.getCityByWikiDataId(locationId)
                return location
        locations=self.locationContext.locateLocation(locationText)
        if len(locations)>0:
            return locations[0]
        else:
            return None
        