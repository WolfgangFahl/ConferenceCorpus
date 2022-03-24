import json

from corpus.eventcorpus import EventDataSource
from corpus.lookup import CorpusLookup, CorpusLookupConfigure
from corpus.web.eventseriesblueprint import EventSeriesCompletion
from tests.datasourcetoolbox import DataSourceTest
from tests.testWebServer import TestWebServer


class TestEventSeriesBlueprint(TestWebServer):
    """
    tests EventSeriesBlueprint
    """

    def testGetEventSeries(self):
        '''
        tests the multiquerying of event series over api
        '''
        jsonStr=self.getResponse("/eventseries/WEBIST?format=json")
        res=json.loads(jsonStr)
        if self.debug:
            print(res)
        self.assertTrue("confref" in res)
        self.assertTrue(len(res["confref"])>15)

    def testEventSeriesCompletion(self):
        """
        tests the event series completion with ghost events
        """
        lod = self.getEventSeries("ICEIS").get("wikicfp")
        jsonStr = self.client.post("/eventseries/complete", data=json.dumps({"wikicfp":lod}, default=str))
        res = json.loads(jsonStr.data.decode())
        if self.debug:
            print(res)
        self.assertTrue("wikicfp" in res)
        self.assertTrue(len(lod) < 20)
        self.assertTrue(len(res["wikicfp"]) > 20)



class TestEventSeriesCompletion(DataSourceTest):
    """
    tests EventSeriesCompletion
    """

    def test_getFrequency(self):
        """
        tests the extraction of series frequency from event records
        """
        testMatrix=[
            {
                "data":self.getEventSeries("ICEIS").get("wikidata"),
                "expected": [{"start": 2001, "end": 2020, "frequency": 1}]
            },
            {
                "data": [{"year":2020, "ordinal":1},
                         {"year":2020, "ordinal":2},
                         {"year":2020, "ordinal":3},
                         {"year":2021, "ordinal":4},
                         {"year":2021, "ordinal":5},
                         {"year":2021, "ordinal":6}],
                "expected":[{"start":2020, "end":2021, "frequency":3}]
            },
            {
                "data": [{"year": 2020, "ordinal": 1},
                        {"year": 2020, "ordinal": 2},
                        {"year": 2020, "ordinal": 3},
                        {"year": 2021, "ordinal": 5},
                        {"year": 2021, "ordinal": 6}],
                "expected": [{"start": 2020, "end": 2021, "frequency": 3}]
            },
            {
                "data": [{"year": 2020, "ordinal": 1},
                        {"year": 2020, "ordinal": 2},
                        {"year": 2020, "ordinal": 3},
                        {"year": 2021, "ordinal": 4},
                        {"year": 2022, "ordinal": 5},
                        {"year": 2023, "ordinal": 6}],
                "expected": [{"start":2020, "end":2021, "frequency":3}, {"start":2021, "end":2023, "frequency":1}]
            }
        ]
        for testRecord in testMatrix:
            actualRes = EventSeriesCompletion.getFrequency(testRecord.get("data"))
            for i, record in enumerate(actualRes):
                self.assertDictEqual(testRecord.get("expected")[i],record)

    def test_isFrequencyConsistent(self):
        """
        tests if frequency consistence is detected correctly
        """
        consistentExample = {
            "ICEIS": self.getEventSeries("ICEIS").get("wikidata"),
            "ISWC":self.getEventSeries("ISWC").get("wikidata"),
            "WEBIST":self.getEventSeries("WEBIST").get("dblp")
        }
        inconsistentExample = {
            "AAAI":self.getEventSeries("AAAI").get("wikidata"),
            "KI":self.getEventSeries("KI").get("wikidata"),
            "ACAL":self.getEventSeries("ACAL").get("wikidata"),
         }
        for series, lod in inconsistentExample.items():
            self.assertFalse(EventSeriesCompletion.isFrequencyConsistent(lod), f"{series} is NOT inconsistent")
        for series, lod in consistentExample.items():
            self.assertTrue(EventSeriesCompletion.isFrequencyConsistent(lod), f"{series} is NOT consistent")


    def test_addGhostEvents(self):
        """
        tests the generation of ghost events
        """
        expectedLod=[{"year": 2018, "ordinal": 1},
                     {"year": 2019, "ordinal": 2},
                     {"year": 2020, "ordinal": 3},
                     {"year": 2021, "ordinal": 4},
                     {"year": 2022, "ordinal": 5},
                     {"year": 2023, "ordinal": 6}]
        lod_missing_start = expectedLod[2:]
        lod_missing_middle = [e for i, e in enumerate(expectedLod) if i not in [1,3,4]]
        self._assertLodEqual(expectedLod, EventSeriesCompletion.addGhostEvents(lod_missing_start))
        self._assertLodEqual(expectedLod, EventSeriesCompletion.addGhostEvents(lod_missing_middle))
        lod_caap=self.getEventSeries("CAAP").get("wikidata")
        self.assertTrue(len(EventSeriesCompletion.addGhostEvents(lod_caap)) == 19)

    def test_extractAndAddOrdinals(self):
        """
        tests if frequency consistence is detected correctly
        ToDo: Extend test and find more corner cases
        """
        lod=self.getEventSeries("AAAI").get("wikidata")
        lod=[d for d in lod if d.get("eventInSeriesId") == 'Q56682083']
        # delete ordinals
        lod_without_ordinal=[ {k:v for k,v in d.items() if k != "ordinal"} for d in lod]
        lodCompleted=EventSeriesCompletion.completeSeries(lod_without_ordinal)
        if self.debug:
            print(lodCompleted)

        # lod_iceis = self.getEventSeries("ICEIS").get("wikidata")
        # lodCompleted_iceis  = EventSeriesCompletion.completeSeries(lod_iceis)
        # print(lodCompleted_iceis )

        lod_webist = self.getEventSeries("WEBIST").get("dblp")
        lodCompleted_webist = EventSeriesCompletion.completeSeries(lod_webist)
        if self.debug:
            print(lodCompleted_webist)


    def test_guessOrdinalBenchmark(self):
        """
        tests the accuracy of the ordinal guessing by guessing the ordinal and than comparing it to the defined ordinal
        """
        return
        if self.inCI():
            return
        lookup=CorpusLookup(lookupIds=['wikidata'])
        lookup.load()
        stats={
            "correct_guess":0,
            "incorrect_guess":0,
            "correct_one_in_set":0,
            "not_in_set":0,
            "no_guess":0,
            "ordinal_not_set": 0
        }
        for test,datasource in lookup.eventCorpus.eventDataSources.items():
            if isinstance(datasource, EventDataSource):
                events=datasource.eventManager.getList()
                for event in events:
                    record=event.__dict__
                    if "ordinal" not in record or event.ordinal is None:
                        stats["ordinal_not_set"]+=1
                        continue
                    correctOrdinal=int(event.ordinal)
                    guessedOrdinal=EventSeriesCompletion.guessOrdinal(record)
                    if len(guessedOrdinal) == 1:
                        if guessedOrdinal[0] == correctOrdinal:
                            stats["correct_guess"]+=1
                        else:
                            stats["incorrect_guess"] += 1
                    elif len(guessedOrdinal) > 1:
                        if correctOrdinal in guessedOrdinal:
                            stats["correct_one_in_set"] += 1
                        else:
                            stats["not_in_set"] += 1
                    else:
                        stats["no_guess"] += 1
        if self.debug:
            print(stats)

    def test_isOrdinalConsistent(self):
        """
        tests if ordinal consistency is correctly detected
        """
        consistentExample={
            "ICEIS":self.getEventSeries("ICEIS").get("wikidata"),
            "WEBIST":self.getEventSeries("WEBIST").get("dblp"),
            "ISWC":self.getEventSeries("ISWC").get("wikidata")
        }
        inconsistentExample={
            "AAAI":self.getEventSeries("AAAI").get("wikidata")
        }
        for series, lod in inconsistentExample.items():
            self.assertFalse(EventSeriesCompletion.isFrequencyConsistent(lod), f"{series} is NOT inconsistent")
        for series, lod in consistentExample.items():
            self.assertTrue(EventSeriesCompletion.isFrequencyConsistent(lod), f"{series} is NOT consistent")

    def test_isOrdinalStyleConsistent(self):
        """
        tests if ordinal style consistency is correctly detected
        """
        consistentExample={
            "ICEIS":self.getEventSeries("ICEIS").get("wikidata"),
            "WEBIST":self.getEventSeries("WEBIST").get("dblp"),
            "ISWC": self.getEventSeries("ISWC").get("wikidata")
        }
        inconsistentExample={
            "AAAI":self.getEventSeries("AAAI").get("wikidata"),
            "CAAP":self.getEventSeries("KI").get("wikidata")
        }
        for series, lod in inconsistentExample.items():
            self.assertFalse(EventSeriesCompletion.isFrequencyConsistent(lod), f"{series} is NOT inconsistent")
        for series, lod in consistentExample.items():
            self.assertTrue(EventSeriesCompletion.isFrequencyConsistent(lod), f"{series} is NOT consistent")

    def test_SeriesConsistencyBenchmark(self):
        """
        tests the accuracy of the ordinal guessing by guessing the ordinal and than comparing it to the defined ordinal
        """
        return
        if self.inCI():
            return
        lookup = CorpusLookup(lookupIds=['wikidata'], configure=CorpusLookupConfigure.configureCorpusLookup)
        lookup.load()
        stats = {
            "ordinalConsistent": 0,
            "ordinalStyleConsistent": 0,
            "frequencyConsistent": 0,
            "considerable": 0,
            "inconsistent": 0,
            "consistent":0 # all three hold
        }
        for test, datasource in lookup.eventCorpus.eventDataSources.items():
            if isinstance(datasource, EventDataSource):
                series = datasource.eventSeriesManager.getList()
                for seriesRecord in series:
                    if seriesRecord.acronym == "WWW":
                        print("Here")
                    events = self.getEventSeries(seriesRecord.acronym)
                    if events is not None and "wikidata" in events:
                        events=events.get("wikidata")
                    else:
                        continue
                    lod=events
                    isOrdinalConsistent = EventSeriesCompletion.isOrdinalConsistent(lod)
                    isOrdinalStyleConsistent = EventSeriesCompletion.isOrdinalStyleConsistent(lod)
                    isFrequencyConsistent = EventSeriesCompletion.isFrequencyConsistent(lod)
                    isConsiderable = EventSeriesCompletion.isConsiderable(lod)
                    isConsistent = isOrdinalConsistent and isOrdinalStyleConsistent and isFrequencyConsistent
                    stats["ordinalConsistent"]+=isOrdinalConsistent
                    stats["ordinalStyleConsistent"] += isOrdinalStyleConsistent
                    stats["frequencyConsistent"] += isFrequencyConsistent
                    stats["consistent"] += isConsistent
                    stats["inconsistent"] += not isConsistent
                    stats["considerable"] += isConsistent and isConsiderable
                    print(f"{seriesRecord.acronym}: OrdinalConsistent[{isOrdinalConsistent}], OrdinalStyleConsistent[{isOrdinalStyleConsistent}], FrequencyConsistent[{isFrequencyConsistent}], Considerable[{isConsiderable}]")
        if self.debug:
            print(stats)

    def _assertLodEqual(self, expectedLod, actualLod):
        """
        Checks if the actual lod and the expected lod are the same.
        Order of the list is important
        """
        for i, expRecord in enumerate(expectedLod):
            self.assertDictEqual(expRecord, actualLod[i])