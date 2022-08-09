import json
from dataclasses import asdict

from spreadsheet.googlesheet import GoogleSheet

from corpus.web.eventseries import MetadataMappings, EventSeriesBlueprint
from tests.testWebServer import TestWebServer


class TestEventSeriesBlueprint(TestWebServer):
    """
    tests EventSeriesBlueprint
    """


    def test_extractWikidataMapping(self):
        """
        extracts wikidata metadata mapping from given google docs url
        """
        return
        url = ""
        gs = GoogleSheet(url)
        gs.open(["Wikidata"])
        sheet = [{k:v for k,v in record.items() if (not k.startswith("Unnamed")) and v is not ''} for record in gs.asListOfDicts("Wikidata")]
        print(sheet)

    def test_MetadataMapping(self):
        mapping = MetadataMappings()
        if self.debug:
            print(asdict(mapping))

    def testGetEventSeries(self):
        '''
        tests the multiquerying of event series over api

        some 17 secs for test
        '''
        jsonStr = self.getResponse("/eventseries/WEBIST?format=json")
        res = json.loads(jsonStr)
        if self.debug:
            print(res)
        self.assertTrue("confref" in res)
        self.assertTrue(len(res["confref"]) > 15)

    def test_getEventSeriesBkFilter(self):
        """
        tests getEventSeries bk filter
        see https://github.com/WolfgangFahl/ConferenceCorpus/issues/55
        """
        testParams = ["85.20", "54.65,54.84", "54.84,85"]
        for testParam in testParams:
            jsonStr = self.getResponse(f"/eventseries/WEBIST?format=json&bk={testParam}")
            res = json.loads(jsonStr)
            self.assertIn("tibkat", res)
            bksPerRecord = [record.get("bk") for record in res.get("tibkat")]
            expectedBks = set(testParam.split(","))
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
        for recordData, bkFilter, expectedNumberOfRecords in testMatrix:
            lod = [{"bk":bk} for bk in recordData]
            EventSeriesBlueprint.filterForBk(lod, bkFilter)
            self.assertEqual(len(lod), expectedNumberOfRecords, f"Tried to filter for {bkFilter} and expected {expectedNumberOfRecords} but filter left {len(lod)} in the list")

    def testTibkatReducingRecords(self):
        """
        tests deduplication of the tibkat records if reduce parameter is set
        """
        positiveTestParams = ["reduce", "reduce=True", "reduce=yes"]
        for testParam in positiveTestParams:
            with self.subTest(msg=f"Testing with {testParam}", testParam=testParam):
                res = self.getJsonResponse(f"/eventseries/AAAI?format=json&{testParam}")
                self.assertIn("tibkat", res)
                self.assertLessEqual(len(res.get("tibkat")), 50)
        negativeTestParams = ["", "reduce=False", "reduce=no"]
        for testParam in negativeTestParams:
            with self.subTest(msg=f"Testing with {testParam}", testParam=testParam):
                res = self.getJsonResponse(f"/eventseries/AAAI?format=json&{testParam}")
                self.assertIn("tibkat", res)
                self.assertGreaterEqual(len(res.get("tibkat")), 400)
