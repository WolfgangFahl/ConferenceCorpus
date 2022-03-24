from datetime import datetime
from functools import partial
from unittest import TestCase
from corpus.event import EventManager, Event, EventSeries, EventSeriesManager, EventStorage


class TestEvent(TestCase):
    '''
    test general features of Event
    '''

    def testFromCsv(self):
        """
        tests csv string to events conversion.
        """
        csvString='''"pageTitle","acronym","ordinal","eventType","subject","startDate","endDate","homepage","title","series","country","region","city","acceptedPapers","submittedPapers","presence","lastEditor","creationDate","modificationDate","year","yearStr"\r
"ICSME 2020","ICSME 2020",36,"Conference","Software engineering","2020-09-27 00:00:00","2020-09-27 00:00:00","","","","","","","","","","","","","",""\r
"WebSci 2019","WebSci 2019",10,"Conference","","2019-06-30 00:00:00","2019-07-03 00:00:00","http://websci19.webscience.org/","10th ACM Conference on Web Science","WebSci","USA","US-MA","Boston",41,120,"online","","","","",""\r
"5GU 2017","5GU 2017",2,"Conference","","2017-06-08 00:00:00","2017-06-09 00:00:00","http://5guconference.org/2017/show/cf-papers","2nd EAI International Conference on 5G for Ubiquitous Connectivity","5GU","Australia","","Melbourne","","","","Wolfgang Fahl","2016-09-25 07:36:02","2020-11-05 12:33:23","",""\r
"IDC 2009","IDC 2009",8,"","","","","","The 8th International Conference on Interaction Design and Children","","","","","","","","","","",2009,"2010"\r
'''
        self.eventManager.fromCsv(csvString=csvString)
        for event in self.eventManager.getList():
            if getattr(event,self.eventManager.primaryKey) == "IDC 2009":
                self.assertEqual(getattr(event,'yearStr'),'2010')

    def testAsCsv(self):
        '''
        test csv conversion of events
        '''
        expectedCsvString='''"pageTitle","acronym","ordinal","eventType","subject","startDate","endDate","homepage","title","series","country","region","city","acceptedPapers","submittedPapers","presence","lastEditor","creationDate","modificationDate","year","yearStr"\r
"ICSME 2020","ICSME 2020",36,"Conference","Software engineering","2020-09-27 00:00:00","2020-09-27 00:00:00","","","","","","","","","","","","","",""\r
"WebSci 2019","WebSci 2019",10,"Conference","","2019-06-30 00:00:00","2019-07-03 00:00:00","http://websci19.webscience.org/","10th ACM Conference on Web Science","WebSci","USA","US-MA","Boston",41,120,"online","","","","",""\r
"5GU 2017","5GU 2017",2,"Conference","","2017-06-08 00:00:00","2017-06-09 00:00:00","http://5guconference.org/2017/show/cf-papers","2nd EAI International Conference on 5G for Ubiquitous Connectivity","5GU","Australia","","Melbourne","","","","Wolfgang Fahl","2016-09-25 07:36:02","2020-11-05 12:33:23","",""\r
"IDC 2009","IDC 2009",8,"","","","","","The 8th International Conference on Interaction Design and Children","","","","","","","","","","",2009,"2009"\r
'''
        actualCsvString=self.eventManager.asCsv()
        self.assertEqual(expectedCsvString,actualCsvString)

    def testAsCsvEventSelection(self):
        '''
        test csv export with event selection callback
        '''
        expectedCsvString='''"pageTitle","acronym","ordinal","homepage","title","eventType","startDate","endDate","series","country","region","city","acceptedPapers","submittedPapers","presence"\r
"WebSci 2019","WebSci 2019",10,"http://websci19.webscience.org/","10th ACM Conference on Web Science","Conference","2019-06-30 00:00:00","2019-07-03 00:00:00","WebSci","USA","US-MA","Boston",41,120,"online"\r
'''
        actualCsvString = self.eventManager.asCsv(
            selectorCallback=partial(self.eventManager.getEventsInSeries, "WebSci"))
        self.assertEqual(expectedCsvString, actualCsvString)

    def setUp(self) -> None:
        sampleEvents = [{
                "pageTitle": "ICSME 2020",
                "acronym": "ICSME 2020",
                "ordinal": 36,
                "eventType": "Conference",
                "subject": "Software engineering",
                "startDate": datetime.fromisoformat("2020-09-27"),
                "endDate": datetime.fromisoformat("2020-09-27")
            },
            {
                "pageTitle": "WebSci 2019",
                "acronym": "WebSci 2019",
                "ordinal": 10,
                "homepage": "http://websci19.webscience.org/",
                "title": "10th ACM Conference on Web Science",
                "eventType": "Conference",
                "startDate": datetime.fromisoformat("2019-06-30"),
                "endDate": datetime.fromisoformat("2019-07-03"),
                "series": "WebSci",
                "country": "USA",
                "region": "US-MA",
                "city": "Boston",
                "acceptedPapers": 41,
                "submittedPapers": 120,
                "presence": "online"
            },
            {
                "acronym": "5GU 2017",
                "city": "Melbourne",
                "country": "Australia",
                "endDate": datetime.fromisoformat("2017-06-09T00:00:00"),
                "eventType": "Conference",
                "homepage": "http://5guconference.org/2017/show/cf-papers",
                "series": "5GU",
                "ordinal": 2,
                "startDate": datetime.fromisoformat("2017-06-08T00:00:00"),
                "title": "2nd EAI International Conference on 5G for Ubiquitous Connectivity",
                # technical attributes - SMW specific
                "pageTitle": "5GU 2017",
                "lastEditor": "Wolfgang Fahl",
                "creationDate": datetime.fromisoformat("2016-09-25T07:36:02"),
                "modificationDate": datetime.fromisoformat("2020-11-05T12:33:23")
            },
            {
                'acronym': "IDC 2009",
                'title': "The 8th International Conference on Interaction Design and Children",
                'pageTitle': 'IDC 2009',
                'ordinal': 8,
                'year': 2009,
                'yearStr': '2009'
            }

        ]
        sampleEventSeries=[{
                'pageTitle': 'AAAI',
                'acronym': 'AAAI',
                'title': 'Conference on Artificial Intelligence',
                'subject': 'Artificial Intelligence',
                'homepage': 'www.aaai.org/Conferences/AAAI/aaai.php',
                'wikidataId': 'Q56682083',
                'dblpSeries': 'aaai',
                'period': 1,
                'unit': 'year'
            },
            {
                'pageTitle': 'WebSci',
                'acronym': 'WebSci',
                'title': 'Web Science Conference'
            }
        ]
        self.eventManager = EventManager(name="TestEventManager", clazz=Event, primaryKey='pageTitle')
        self.eventManager.fromLoD(sampleEvents)
        self.eventSeriesManager = EventSeriesManager(name="TestEventSeriesManager", clazz=EventSeries)
        self.eventSeriesManager.fromLoD(sampleEventSeries)
        self.eventManager.linkSeriesAndEvent(self.eventSeriesManager)
        
    def testGetLookupAcronym(self):
        ''' test fixing acronyms that contain no year '''
        eventinfos = [
            {"acronym":"FLAM 2013"},
            {"acronym": "IPTC", "year": 2014},
            {"acronym": "COMET", "year": "2012"},
            {"title":"Proceedings of the 50th North American Chemical Residue Workshop (NACRW)", "event": "NACRW", "year": 2013}
        ]
        fixed = ["FLAM 2013", "IPTC 2014", "COMET 2012", "NACRW 2013"]  
        for idx, eventinfo in enumerate(eventinfos):
            event = Event()
            event.fromDict(eventinfo)
            event.getLookupAcronym()
            self.assertEqual(fixed[idx], event.lookupAcronym)
        
    def testWikiSon(self):
        ''' test WikiSon format '''
        eventinfos = [
            { "acronym": "AAMAS 2015", 
              "city": "Istanbul", 
              "country": "Turkey", 
              "creation_date": "2016-09-29 18:38:27", 
              "event": "AAMAS 2015", "foundBy": "AAMAS 2015", "homepage": "http://www.aamas-conference.org/Proceedings/aamas2015/", "modification_date": "2016-09-29 18:38:27", "series": "AAMAS", "source": "OPEN RESEARCH", "start_date": "2015-01-01 00:00:00", "title": 'AAMAS 2015', "url": "https://www.openresearch.org/wiki/AAMAS 2015" }
        ]
        for eventinfo in eventinfos:
            eventDicts=[]
            event = Event()
            event.fromDict(eventinfo)
            #event.getLookupAcronym()
            eventDicts.append(event.__dict__)
        wikison=EventManager.asWikiSon(eventDicts)    
        if self.debug:
            print(wikison)
        self.assertTrue('{{Event' in wikison)
        self.assertTrue('|event=AAMAS 2015' in wikison)