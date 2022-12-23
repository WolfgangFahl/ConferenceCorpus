import unittest
from typing import List

import pandas as pd
from geograpy.locator import City
from lodstorage.lod import LOD

from tests.basetest import BaseTest
from corpus.event import EventStorage
from corpus.eventseriescompletion import EventSeriesCompletion
from corpus.location import LocationLookup
from plp.parsing import Tokenizer
from plp.signature import AcronymCategory

@unittest.skip("Tests are in development for a matching training set generation")
class TestMatching(BaseTest):
    """
    tests the matching of event records from different data sources based on the event signature
    """

    def setUp(self,debug=False,profile=True):
        super(TestMatching, self).setUp(debug, profile)
        self.locationLookup = LocationLookup()
        self.testSeries = ["AAAI", "ACII", "ACISP", "ADMA", "AIED", "WEBIST", "AIME", "CAIP", "CC", "FASE", "ICEIS", "ICIAP", "ICIAR", "TACAS", "VNC"]
        self.sqlDB = EventStorage.getSqlDB()

    def getEventRecordOfOrclone(self) -> List[dict]:
        """
        get event records of orclone
        """
        sqlQuery = f"""SELECT acronym, year, ordinal, inEventSeries AS 'series',inEventSeries AS 'seriesOpenresearchId', startDate, endDate, city, country, title, source, eventId AS 'openresearchId', wikicfpId, wikidataId, TibKatId, DblpConferenceId, gndId FROM event_orclone"""
        lod = self.sqlDB.query(sqlQuery)
        return lod

    def getEventRecordOfDblp(self) -> List[dict]:
        """
        get event records of dblp
        """
        sqlQuery = f"""SELECT acronym, year, ordinal, series, startDate, endDate, location, cityWikidataid, countryWikidataid, title, source, eventId AS 'DblpConferenceId' FROM event_dblp"""
        lod = self.sqlDB.query(sqlQuery)
        return lod

    def getEventRecordOfTibkat(self) -> List[dict]:
        """
        get event records of tibkat
        """
        sqlQuery = f"""SELECT acronym, year, ordinal, startDate, endDate, location, cityWikidataid, countryWikidataid, title, source, eventId AS 'TibKatId' FROM event_tibkat"""
        lod = self.sqlDB.query(sqlQuery)
        return lod

    def getEventRecordOfGnd(self, parseAcronym:bool=False) -> List[dict]:
        """
        get the gnd event records

        Args:
            parseAcronym: If True parse the Acronym from the title if the acronym is not set
        """
        sqlQuery = f"""SELECT acronym, year, ordinal, startDate, endDate, location, cityWikidataid, countryWikidataid, title, source, eventId AS 'gndId' FROM event_gnd"""
        lod = self.sqlDB.query(sqlQuery)
        if parseAcronym:
            tokenizer = Tokenizer([AcronymCategory()])
            for d in lod:
                if d.get("acronym", None) is None:
                    title = d.get("title")
                    tokenSeq = tokenizer.tokenize(title, "gnd")
                    acronyms = tokenSeq.getTokenOfCategory("acronym")
                    if len(acronyms) == 1:
                        d["acronym"] = acronyms[0].value
        return lod

    def getEventRecordOfWikidata(self) -> List[dict]:
        """
        get event records of wikidata
        """
        sqlQuery = f"""SELECT acronym, year, ordinal, startDate, endDate, cityWikidataid, countryWikidataid, title, eventInSeries AS 'series', eventInSeriesId AS 'seriesWikidataId', source, eventId AS 'wikidataId' FROM event_wikidata"""
        lod = self.sqlDB.query(sqlQuery)
        return lod

    def getEventRecordOfWikicfp(self) -> List[dict]:
        """
        get event records of wikicfp
        """
        sqlQuery = f"""SELECT acronym, year, ordinal, startDate, endDate, cityWikidataid, countryWikidataid, title, series, seriesId AS 'seriesWikicfpId', source, eventId AS 'wikicfpId' FROM event_wikicfp"""
        lod = self.sqlDB.query(sqlQuery)
        return lod

    def normalizeLocation(self, lod:List[dict]) -> List[dict]:
        """
        Normalizes the city and country property to wikidataIds
        """
        for d in lod:
            city = d.get("city", d.get("location", None))
            country = d.get("country", None)
            if city is not None:
                qCity = self.locationLookup.lookupGeograpy(city.replace("/", ", "))
                if isinstance(qCity, City):
                    d["cityWikidataid"] = qCity.wikidataid
                    d["countryWikidataid"] = qCity.country.wikidataid

            elif country is not None:
                qCountry = self.locationLookup.lookup(country.replace("/", ", "))
                d["country"] = qCountry
        return lod

    def getSignatureCompleteSeries(self, eventRecords:List[dict], minNumberOfEvents:int=None) -> List[str]:
        """
        Returns a list of series for which all the events have a complete signature
        Args:
            eventRecords: list of event records

        Returns:
            list of series acronyms
        """
        res = {}
        for eventRecord in eventRecords:
            series = eventRecord.get("series")
            if series is None:
                continue
            elif series not in res:
                res[series] = True
            signatureProps = ["acronym", "year", "endDate", "ordinal",  "startDate", "title"]
            locationIsSet = eventRecord.get("location") or (eventRecord.get("country") and eventRecord.get("city"))
            signatureComplete = all([eventRecord.get(prop) is not None for prop in signatureProps])
            res[series] = res[series] and signatureComplete and locationIsSet
        signatureCompleteSeries = [series for series, signatureComplete in res.items() if signatureComplete]
        if minNumberOfEvents is not None:
            signatureCompleteSeries = [series
                                   for series in signatureCompleteSeries
                                   if
                                   len([er for er in eventRecords if er.get("series") == series]) > minNumberOfEvents]
        return signatureCompleteSeries

    def testGetOrSeriesWithSignatureCompleteEvents(self) -> (List[dict], List[str]):
        """
        Determines all series which have signature complete events
        """
        orEventRecords = self.getEventRecordOfOrclone()
        self.normalizeLocation(orEventRecords)
        seriesAcronyms = self.getSignatureCompleteSeries(orEventRecords, 4)
        orEventRecords = [eventRecord for eventRecord in orEventRecords if eventRecord.get("series") in seriesAcronyms]
        return orEventRecords, seriesAcronyms

    def convertTitleToWords(self, title:str) -> List[str]:
        """
        converts given title to a list of words. Special chars are removed before.
        Args:
            title: title to convert

        Returns:
            List of words in the title
        """
        if title is None:
            return []
        for char in "/()#,;-@'´`":
            title = title.replace(char, " ")
        return title.split(" ")

    def testCreateTrainingDataSet(self, includedSeries:List[str]=None):
        """
        creates a training/validation dataset to test matching algorithms for event records.

        Dataset description:
        the training set consists only of event records that have at least three confirmed matches to other data sources
        it is based on openresearch records as they have been manually curated

        Args:
            includedSeries: list of series that should be included in the dataset If None include all signature complete series in openresearch
        """
        if includedSeries is None:
            orEventRecords, seriesAcronyms = self.testGetOrSeriesWithSignatureCompleteEvents()
        else:
            orEventRecords = self.getEventRecordOfOrclone()
            seriesAcronyms = includedSeries
            orEventRecords = [eventRecord
                              for eventRecord in orEventRecords
                              if eventRecord.get("series") in seriesAcronyms]
        seriesAcronymsLower = [seriesAcronym.lower() for seriesAcronym in seriesAcronyms]
        # Get the eventRecords from the other sources → reduce them to the events of series in seriesAcronyms
        # dblp
        dblpEventRecords = self.getEventRecordOfDblp()
        dblpEventRecordsBySeries = LOD.getLookup(dblpEventRecords, "series", withDuplicates=True)
        dblpEventRecordsBySeries = {seriesAcronym:events
                                    for seriesAcronym, events in dblpEventRecordsBySeries.items()
                                    if seriesAcronym in seriesAcronymsLower}
        dblpEventRecords = []
        for seriesAcronym, events in dblpEventRecordsBySeries.items():
            reducedRecords = EventSeriesCompletion.filterDuplicatesByTitle(events)
            dblpEventRecords.extend(reducedRecords)
        # tibkat
        tibkatEventRecordsRaw = self.getEventRecordOfTibkat()
        tibkatEventRecords = []
        for seriesAcronym in seriesAcronyms:
            eventRecords = [eventRecord
                            for eventRecord in tibkatEventRecordsRaw
                            if (eventRecord.get("series", None) is not None
                                and seriesAcronym.lower() in self.convertTitleToWords(eventRecord.get("series").lower()))
                            or (eventRecord.get("acronym", None) is not None
                                and seriesAcronym.lower() in self.convertTitleToWords(eventRecord.get("acronym").lower()))]
            tibkatEventRecords.extend(EventSeriesCompletion.filterDuplicatesByTitle(eventRecords))
        # gnd
        gndEventRecordsRaw = self.getEventRecordOfGnd(parseAcronym=True)
        gndEventRecords = []
        for seriesAcronym in seriesAcronyms:
            eventRecords = [eventRecord
                            for eventRecord in gndEventRecordsRaw
                            if eventRecord.get("acronym", None) is not None
                            and seriesAcronym.lower() in self.convertTitleToWords(eventRecord.get("acronym").lower())]
            gndEventRecords.extend(eventRecords)
        # wikidata
        wikidataEventRecordsRaw = self.getEventRecordOfWikidata()
        wikidataEventRecords = []
        for seriesAcronym in seriesAcronyms:
            eventRecords = [eventRecord
                            for eventRecord in wikidataEventRecordsRaw
                            if (eventRecord.get("series", None) is not None
                                and seriesAcronym.lower() in self.convertTitleToWords(eventRecord.get("series").lower()))
                             or (eventRecord.get("acronym", None) is not None
                                 and seriesAcronym.lower() in self.convertTitleToWords(eventRecord.get("acronym").lower()))]
            wikidataEventRecords.extend(eventRecords)
        # wikicfp
        wikicfpEventRecordsRaw = self.getEventRecordOfWikicfp()
        wikicfpEventRecords = []
        for seriesAcronym in seriesAcronyms:
            eventRecords = [eventRecord
                            for eventRecord in wikicfpEventRecordsRaw
                            if eventRecord.get("acronym", None) is not None
                            and seriesAcronym.lower() in self.convertTitleToWords(
                    eventRecord.get("acronym").lower())]
            wikicfpEventRecords.extend(eventRecords)

        eventRecords = [*orEventRecords,
                        *dblpEventRecords,
                        *tibkatEventRecords,
                        *gndEventRecords,
                        *wikidataEventRecords,
                        *wikicfpEventRecords]
        df = pd.DataFrame.from_records(eventRecords)
        from pathlib import Path

        filepath = Path('/tmp/ccMatching/trainingSet2.csv')
        filepath.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(filepath)
        df.to_csv(filepath)

    def testTrainingSetWithAAAI(self):
        self.testCreateTrainingDataSet(includedSeries=["ACISP"])

