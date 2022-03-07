'''
Created on 2021-08-11

@author: wf
'''
#from lodstorage.entity import EntityManager
from geograpy.locator import LocationContext
from corpus.nominatim import NominatimWrapper
import sys
class LocationLookup:
    '''
    lookup locations
    '''
    preDefinedLocations={
        "Not Known": None,
        "Online": None,
        "Virtual Event, USA": None,
        "Albuquerque, New Mexico, USA":"Q34804",
        "Alexandria, Virginia, USA":"Q88",
        "Alexandria, VA": "Q88",
        "Amsterdam": "Q727",
        "Amsterdam, Amsterdam": "Q727",
        "Amsterdam Netherlands": "Q727",
        "Amsterdam, Netherlands": "Q727",
        "Amsterdam, The Netherlands":"Q727",
        "Bergen, Norway":"Q26793",
        "Bremen, Germany": "Q24879",
        "Brussels, Belgium": "Q239",
        "Cancun, Mexico":"Q8969",
        "Cancún, Mexico": "Q8969",
        "Cambridge, United Kingdom": "Q21713103",
        "Cambridge, UK": "Q21713103",
        "Cambridge, USA": "Q49111",
        "Cambridge, MA":"Q49111",
        "Cambridge, Massachusetts": "Q49111",
        "Cambridge, Massachusetts, USA":"Q49111",
        "Cambridge, MA, USA":"Q49111",
        "Charleston, South Carolina, USA":"Q47716",
        "Gdansk, Poland":"Q1792",
        "Heraklion, Crete, Greece":"Q160544",
        "Los Angeles California": "Q65",
        "Los Angeles CA USA": "Q65",
        "Luxembourg, Luxembourg":"Q1842",
        "Macau, Macau, China":"Q14773",
        "Marina del Rey, CA": "Q988140",
        "Monterrey, Mexico":"Q81033",
        "Montreal, QC": "Q340",
        "Montréal, QC": "Q340",
        "Montreal, QC, Canada": "Q340",
        "Montrèal, Canada": "Q340",
        "New Brunswick, New Jersey, USA":"Q138338",
        "New Brunswick, New Jersey": "Q138338",
        "New Delhi": "Q987",
        "New Delhi, India": "Q987",
        "New Orleans, LA": "Q34404",
        "Palo Alto, USA": "Q47265",
        "Palo Alto, CA": "Q47265",
        "Palo Alto, California": "Q47265",
        "Palo Alto, California, USA": "Q47265",
        "Pasadena, California, USA":"Q485176",
        "Phoenix": "Q16556",
        "Phoenix, AZ": "Q16556",
        "Phoenix, Arizona": "Q16556",
        "Phoenix AZ USA": "Q16556",
        "Phoenix, Arizona, USA": "Q16556",
        "Phoenix, USA":  "Q16556",
        "Phoenix, USA": "Q16556",
        "Phoenix, AZ, USA": "Q16556",
        "Salamanca, Spain": "Q15695",
        "Santa Barbara, California": "Q159288",
        "Santa Barbara, CA": "Q159288",
        "Santa Barbara, CA, USA": "Q159288",
        "Santa Barbara CA USA":  "Q159288",
        "Santa Barbara, USA": "Q159288",
        "Santa Barbara, California, USA": "Q159288",
        "Santa Fe, New Mexico": "Q38555",
        "Santa Fe, NM, USA": "Q38555",
        "Santa Fe, New Mexico, USA": "Q38555",
        "Santa Fe, USA": "Q38555",
        "Santa Fe, New Mexico, United States": "Q38555",
        "Skovde, Sweden": "Q21166",
        "Snowbird, Utah, USA": "Q3487194",
        "St. Louis, MO, USA": "Q38022",
        "St. Petersburg": "Q656",
        "Saint-Petersburg, Russia":"Q656",
        "Thessaloniki": "Q17151",
        "Thessaloniki, Greece": "Q17151",
        "Toronto, ON": "Q172",
        "Toronto, Ontario": "Q172",
        "Toronto, Ontario, Canada": "Q172",
        "Toronto, Canada": "Q172",
        "Trondheim, Norway":"Q25804",
        "Valencia": "Q8818",
        "Valencia, Spain": "Q8818",  
        "Valencia, Valencia, Spain": "Q8818",  
        "York, UK":"Q42462"
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
        "Gothenburg Sweden": "Q25287",
        
        "Zurich, Switzerland": "Q72",
        "Barcelona Spain": "Q1492",
        "Vienna Austria": "Q1741",
        "Seoul Republic of Korea": "Q8684",
        "Seattle WA USA": "Q5083",
        "Singapore Singapore":"Q334",
        "Tokyo Japan": "Q1490",
        "Vancouver BC Canada": "Q24639",
        "Vancouver British Columbia Canada": "Q24639",
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
        self.nominatimWrapper=NominatimWrapper(cacheDir=cacheDir)
        
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
        '''
        lookup the location for the given locationText (if any)
        
        Args:
            locationText(str): the location text to search for
            
        Return:
            the location by first finding the wikidata id for the location text and then looking up the location
        '''
        location=None
        wikidataId=self.nominatimWrapper.lookupWikiDataId(locationText)
        if wikidataId is not None:
            location=self.getCityByWikiDataId(wikidataId)
        return location
        
    def lookup(self,locationText:str,logFile=sys.stdout):
        '''
        lookup a location based on the given locationText
        
        Args:
            locationText(str): the location to lookup
            logFile: the logFile to use - default is sys.stdout
        '''
        if locationText in LocationLookup.preDefinedLocations:
            locationId=LocationLookup.preDefinedLocations[locationText]
            if locationId is None:
                return None
            else:
                location=self.getCityByWikiDataId(locationId)
                if location is None:
                    print(f"❌❌-predefinedLocation {locationText}→{locationId} wikidataId not resolved",file=logFile)
                return location
        lg=self.lookupGeograpy(locationText)
        ln=self.lookupNominatim(locationText)
        if ln is not None and lg is not None and not ln.wikidataid==lg.wikidataid:
            print(f"❌❌{locationText}→{lg}!={ln}",file=logFile)
            return None
        return lg
        
    def lookupGeograpy(self,locationText:str):
        '''
        lookup the given location by the given locationText
        '''
        locations=self.locationContext.locateLocation(locationText)
        if len(locations)>0:
            return locations[0]
        else:
            return None
        