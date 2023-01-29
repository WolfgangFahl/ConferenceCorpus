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
    predefinedLocations={}
    
    @classmethod
    def initPredefinedLocations(cls):
        locMap={
            "Not Known": None,
            "Online": None,
            "Virtual": None,
            "Virtual, USA": None,
            "Virtual Event, USA": None,
            "Amsterdam": "Q727",
            "Amsterdam, Amsterdam": "Q727",
            "Amsterdam Netherlands": "Q727",
            "Amsterdam, Netherlands": "Q727",
            "Amsterdam, The Netherlands":"Q727",
            "Amsterdam The Netherlands": "Q727",
            "Będlewo, Poland": "Q5005546",
            "Bergen, Norway":"Q26793",
            "Bremen, Germany": "Q24879",
            "Brussels, Belgium": "Q239",
            "Brussels Belgium": "Q239",
            "Cancun, Mexico":"Q8969",
            "Cancún, Mexico": "Q8969",
            "Gdansk, Poland":"Q1792",
            "Heraklion, Crete, Greece":"Q160544",
            "Красноярск": "Q919",
            "Luxembourg, Luxembourg":"Q1842",
            "Macau, Macau, China":"Q14773",
            "Marina del Rey, CA": "Q988140",
            "Monterrey, Mexico":"Q81033",
            "Москва": "Q649",
            "New Delhi": "Q987",
            "New Delhi, India": "Q987",
            "Новосибирск":"Q883",
            "Salamanca, Spain": "Q15695",
            "Skovde, Sweden": "Q21166",
            "St. Petersburg": "Q656",
            "Санкт-Петербург": "Q656",
            "Saint-Petersburg, Russia":"Q656",
            "Thessaloniki": "Q17151",
            "Thessaloniki, Greece": "Q17151",
            "Trondheim, Norway":"Q25804",
            "Valencia": "Q8818",
            "Valencia, Spain": "Q8818",  
            "Valencia, Valencia, Spain": "Q8818",  
            "York, UK":"Q42462"
        }
        for city,region,regionCode,countryCode,country,wikiDataId in [
            ("Albuquerque","New Mexico","NM","USA","United States","Q34804"),
            ("Alexandria","Virginia","VA","USA","United States","Q88"),
            ("Cambridge",None,None,"UK","United Kingdom","Q21713103"),
            ("Cambridge","Massachusetts","MA","USA","United States","Q49111"),
            ("Charleston","South Carolina","SC","USA","United States","Q47716"),
            ("Lake Louise","Alberta","AB","CA","Canada","Q12826048"),
            ("Los Angeles","California","CA","USA","United States","Q65"),
            ("Miami Beach","Florida", "FL", "USA","United States","Q201516"),
            ("Montreal","Quebec","QC","CA","Canada","Q340"),
            ("Montréal","Quebec","QC","CA","Canada","Q340"),
            ("New Brunswick","New Jersey","NJ","USA","United States","Q138338"),
            ("New Port Beach","California","CA","USA","United States","Q268873"),
            ("Newport Beach","California","CA","USA","United States","Q268873"),
            ("New Orleans","Louisiana","LA","USA","United States","Q34404"),
            ("New York","New York","NY","USA","United States", "Q60"),
            ("Palo Alto","California","CA","USA","United States","Q47265"),
            ("Pasadena","California","CA","USA","United States","Q485176"),
            ("Phoenix","Arizona","AZ","USA","United States", "Q16556"),
            ("San Diego", "California","CA","USA","United States", "Q16552"),
            ("San Francisco","California","CA","USA","United States", "Q62"),
            ("San Jose","California","CA","USA","United States", "Q16553"),
            ("Santa Barbara","California","CA","USA","United States", "Q159288"),
            ("Santa Fe","New Mexico","NM","USA","United States","Q38555"),
            ("Snowbird","Utah","UT","USA","United States","Q3487194"),
            ("St. Louis","Missouri","MO","USA","United States", "Q38022"),
            ("Toronto","Ontario","ON","CA","Canada", "Q172"),
            ("Waikiki, Honolulu","Hawaii","HI","USA","United States","Q254861")
        ]:
            terms=[
                f"{city}, {country}",
                f"{city}, {countryCode}"
            ]
            if region is not None:
                terms.extend([
                    f"{city}, {region}",
                    f"{city} {region}",
                    f"{city}, {regionCode}",
                    f"{city} {regionCode}",
                    f"{city}, {region}, {country}",
                    f"{city} {region} {country}"
                    f"{city}, {region}, {countryCode}",
                    f"{city} {region} {countryCode}",
                    f"{city}, {regionCode}, {country}",
                    f"{city} {regionCode} {country}",
                    f"{city}, {regionCode}, {countryCode}",
                    f"{city} {regionCode} {countryCode}"
                ])
            for term in terms:
                locMap[term]=wikiDataId
        cls.preDefinedLocations=locMap
        cls.other={
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
        cls.predefinedLocations=locMap
    

    def __init__(self):
        '''
        Constructor
        '''
        LocationLookup.initPredefinedLocations()
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
        