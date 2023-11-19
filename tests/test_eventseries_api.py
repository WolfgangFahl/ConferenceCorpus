import json
from dataclasses import asdict

from spreadsheet.googlesheet import GoogleSheet

from corpus.web.eventseries import MetadataMappings, EventSeriesAPI
from tests.datasourcetoolbox import DataSourceTest 
from corpus.lookup import CorpusLookup

class TestEventSeriesAPI(DataSourceTest):
    """
    tests EventSeriesBlueprint
    """
    @classmethod
    def setUpClass(cls)->None:
        super(TestEventSeriesAPI, cls).setUpClass()
        cls.lookup=CorpusLookup()
        
    def setUp(self, debug=False, profile=True, timeLimitPerTest=10.0):
        DataSourceTest.setUp(self, debug=debug, profile=profile, timeLimitPerTest=timeLimitPerTest)
        self.lookup=TestEventSeriesAPI.lookup
        
    def testLookup(self):
        """
        check the lookup
        """
        self.assertTrue(self.lookup is not None)
        debug=self.debug
        datasource_count=len(self.lookup.eventCorpus.eventDataSources)
        if debug:
            print(f"found {datasource_count} datasources")
        self.assertTrue(datasource_count>3)
        
        
    def test_extractWikidataMapping(self):
        """
        extracts wikidata metadata mapping from given google docs url
        """
        url = "https://docs.google.com/spreadsheets/d/1-6llZSTVxNrYH4HJ0DotMjVu9cTHv2WnT_thfQ-3q14"
        gs = GoogleSheet(url)
        gs.open(["Wikidata"])
        lod=gs.asListOfDicts("Wikidata")
        debug=self.debug
        #debug=True
        if debug:
            print(f"found {len(lod)} events")
            print(json.dumps(lod,indent=2))
        self.assertEqual(23,len(lod))
        pass
    
        #sheet = [{k:v for k,v in record.items() if (not k.startswith("Unnamed")) and v is not ''} for record in ]
        #print(sheet)

    def test_MetadataMapping(self):
        """
        test the metadata mapping
        """
        mapping = MetadataMappings()
        debug=self.debug
        #debug=True
        mapping_dict=asdict(mapping)
        if debug:
            print(json.dumps(mapping_dict,indent=2))
        self.assertTrue("WikidataMapping" in mapping_dict)
        
    def testGetEventSeries(self):
        '''
        tests the multiquerying of event series over api

        some 17 secs for test
        '''
        es_api=EventSeriesAPI(self.lookup)
        dict_of_lods=es_api.getEventSeries(name="WEBIST")
        debug=self.debug
        #debug=True
        if debug:
            print(json.dumps(dict_of_lods,indent=2,default=str))
            
        self.assertTrue("confref" in dict_of_lods)
        self.assertTrue(len(dict_of_lods["confref"]) > 15)

    def test_getEventSeriesBkFilter(self):
        """
        tests getEventSeries bk filter
        see https://github.com/WolfgangFahl/ConferenceCorpus/issues/55
        """
        bks_list = ["85.20", "54.65,54.84", "54.84,85"]
        es_api=EventSeriesAPI(self.lookup)
        for bks in bks_list:
            res=es_api.getEventSeries(name="WEBIST", bks=bks)
            self.assertIn("tibkat", res)
            bksPerRecord = [record.get("bk") for record in res.get("tibkat")]
            expectedBks = set(bks.split(","))
            for rawBks in bksPerRecord:
                self.assertIsNotNone(rawBks)
                bks = set(rawBks.split("⇹"))
                bks = bks.union({bk.split(".")[0] for bk in bks})
                self.assertTrue(bks.intersection(expectedBks))

    def test_filterForBk(self):
        """
        tests filterForBk
        """
        testMatrix = [
            (['54.84⇹85.20', '54.84⇹85.20', '54.84⇹81.68⇹85.20⇹88.03⇹54.65', '85.20'], ["54"], 3),
            (['54.84⇹85.20', '54.84⇹85.20', '54.84⇹81.68⇹85.20⇹88.03⇹54.65', '85.20'], ["54","85"], 4),
            (['54.84⇹85.20', '54.84⇹85.20', '54.84⇹81.68⇹85.20⇹88.03⇹54.65', '85.20'], ["85.20"], 4),
            (['54.84⇹85.20', '54.84⇹85.20', '54.84⇹81.68⇹85.20⇹88.03⇹54.65', '85.20'], ["02"], 0),
            (['54.84⇹85.20', '54.84⇹85.20', '54.84⇹81.68⇹85.20⇹88.03⇹54.65', '85.20'], ["81.68","88.03"], 1),
            (['54.84⇹85.20', '54.84⇹85.20', None, '85.20'], ["54"], 2),
            (['54.84⇹85.20', '54.84⇹85.20', None, '85.20'], ["54","null"], 3),
            (['54.84⇹85.20', '54.84⇹85.20', None, '85.20'], ["null"], 1),
            (['54.84⇹85.20', '54.84⇹85.20', None, '85.20'], ["none"], 1),
        ]
        es_api=EventSeriesAPI(self.lookup)
        for recordData, bkFilter, expectedNumberOfRecords in testMatrix:
            lod = [{"bk":bk} for bk in recordData]
            es_api.filterForBk(lod, bkFilter)
            self.assertEqual(len(lod), expectedNumberOfRecords, f"Tried to filter for {bkFilter} and expected {expectedNumberOfRecords} but filter left {len(lod)} in the list")

    def testTibkatReducingRecords(self):
        """
        tests deduplication of the tibkat records if reduce parameter is set
        """
        name="AAAI"
        expected={
            False: 400,
            True: 50
        }
        es_api=EventSeriesAPI(lookup=self.lookup)
        for reduce in (True,False):
            with self.subTest(msg=f"Testing with reduce={reduce}", testParam=reduce):
                res=es_api.getEventSeries(name=name, reduce=reduce)
                self.assertIn("tibkat", res)
                tibkat_count=len(res.get("tibkat"))
                should=expected[reduce]<=tibkat_count
                if reduce:
                    should=not should
                self.assertTrue(should)