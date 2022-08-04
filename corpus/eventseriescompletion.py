'''
Created on 2022-04-03

@author: wf
'''
import re
from typing import List, Tuple, Dict

from lodstorage.lod import LOD

from ptp.signature import OrdinalCategory


class EventSeriesCompletion(object):
    '''
    complete a series of events from different datasources 
    '''
    tokenizer=None
    
    def __init__(self):
        '''
        Constructor
        '''            
    
    
    @classmethod
    def getCompletedBlankSeries(cls, lod: List[dict], debug: bool = False) -> list:
        """
        gets all blank entries of a series from the different records that are given.
        It is expected that each lod comes from a  different datasource
        Args:
            lods: list of event records

        Returns:
            List of completed year ordinal pairs, or empty list if given lod can not be completed
        """
        yearOrdinalPair = {(r.get('year'), r.get("ordinal")) for r in lod }
        completeYearOrdinalPair = list({(year, ordinal) for year, ordinal in yearOrdinalPair if year is not None and ordinal is not None})
        completeYearOrdinalPair.sort(key=lambda r: r[0] if r[0] is not None else 0)
        cleanedYOP = [completeYearOrdinalPair[0]]
        ordinal = completeYearOrdinalPair[0][1]
        for year, ord in completeYearOrdinalPair[1:]:
            if ordinal < ord:
                cleanedYOP.append((year, ord))
                ordinal = ord
        completeYearOrdinalPair = cleanedYOP
        ordByYear = {}
        for year, ord in completeYearOrdinalPair:
            if year in ordByYear:
                ordByYear[year].append(ord)
            else:
                ordByYear[year] = [ord]
        if debug:
            yearsWithKnownOrd = {year for year, ordinal in completeYearOrdinalPair}
            ordinalWithKnownYear = {ordinal for year, ordinal in completeYearOrdinalPair}
            yearWithUnknownOrdinal = {year for year, ordinal in yearOrdinalPair if year not in yearsWithKnownOrd and year is not None}
            ordinalWithUnkownYear = {ordinal for year, ordinal in yearOrdinalPair if ordinal not in ordinalWithKnownYear and ordinal is not None}
            print("Years without ordinal", yearWithUnknownOrdinal)
            print("Ordinals with unknown Year", ordinalWithUnkownYear)
            print("Year ordinal pairs: ", completeYearOrdinalPair)
            print("Ordinals by year: ", ordByYear)
        hasMultipleOrdinalsForAYear = any([len(ords)>1 for ords in ordByYear.values()])
        if hasMultipleOrdinalsForAYear:
            if debug:
                print("Multiple ordinals per year → can not complete series")
            return []
        else:
            frequency = cls.getFrequency(completeYearOrdinalPair)
            if frequency:
                # series is frequency consistent
                lastKnownEvent = completeYearOrdinalPair[-1]
                inception = lastKnownEvent[0] - (frequency * lastKnownEvent[1])
                return [(inception+(i*frequency), i) for i in range(1,lastKnownEvent[1]+1)]
        return []

    @classmethod
    def getFrequency(cls, yearOrdinalPairs:List[Tuple[int, int]], debug:bool=False) -> int:
        """
        Determines the Frequency of the given year ordinal pairs.
        Only returns the frequency if it is consistent over the complete series.

        Args:
            yearOrdinalPairs (list): list of year ordinal pairs for which the frequency should be determined

        Returns:
            Returns the frequency or 0 if inconsistent or if the frequency could not be determined
        """
        if len(yearOrdinalPairs) <= 1:
            return 0
        yearOrdinalPairs.sort(key=lambda r: r[0] if r[0] is not None else 0)
        ordMonotonicallyIncreasing = all([ord < yearOrdinalPairs[i+1][1] for i, (year, ord) in enumerate(yearOrdinalPairs[:-1])])
        if not ordMonotonicallyIncreasing:
            return 0
        firstKnownEvent = yearOrdinalPairs[0]
        lastKnownEvent = yearOrdinalPairs[-1]
        if debug:
            print("First:", firstKnownEvent, "Last:", lastKnownEvent, "#YearOrdPairs:", len(yearOrdinalPairs))#
        timeDelta = lastKnownEvent[0] - firstKnownEvent[0]
        ordinalDelta = lastKnownEvent[1] - firstKnownEvent[1]
        frequency = timeDelta / ordinalDelta
        yearsBetweenEvents = {(year - yearOrdinalPairs[i][0])/(ord - yearOrdinalPairs[i][1]) for i, (year, ord) in enumerate(yearOrdinalPairs[1:])}
        if frequency.is_integer() and len(yearsBetweenEvents) == 1 and int(frequency) in yearsBetweenEvents:
            return int(frequency)
        return 0


    @staticmethod
    def filterDuplicatesByTitle(lod: List[dict], debug: bool = False) -> List[dict]:
        """
        tries to filter out duplicate event records
        currently only for tibkat and dblp records
        Args:
            lod(List[dict]): List of event records from one sources
            debug(bool): if True show debug messages

        Returns:
            List[dict]
        """
        byYear = LOD.getLookup(lod, "year", withDuplicates=True)
        res = []
        for year, records in byYear.items():
            if len(records) > 1:
                recordsRanked = [(TitleScore.getScore(record.get("title")), record) for record in records]
                recordsRanked.sort(key=lambda pair:pair[0], reverse=True)
                if debug:
                    print(f"==={year}===")
                    for score, record in recordsRanked:
                        print(f"* {score} - '{record.get('title')}'")
                maxScore = recordsRanked[0][0]
                records = [record for score, record in recordsRanked if score == maxScore]
                res.extend(records)
            else:
                res.append(records[0])
        return res


class TitleScore:
    """
    Calculates a rating for an event title
    A higher score represents a better fit of the record as first/correct record for an event with multiple records
    """
    VOLUME_LOOKUP = OrdinalCategory()

    @classmethod
    def getScore(cls, title:str)-> float:
        """
        calc title score
        Args:
            title: event title

        Returns:
            float - score
        """
        if title is None:
            return 0.0
        score = cls._hasProceeding(title) + cls._hasEventType(title)
        volume = cls._getVolume(title)
        if volume:
            score += 1/volume
        score += (1/max(1, cls._countSpecialCharacters(title))) / 2
        return score

    @classmethod
    def _getVolume(cls, title:str) -> int:
        #ToDo: Migrate to VolumeCategory parsing
        volumePattern = r"\[?([Vv]ol\.|[Vv]olume|[Pp]t\.|[Pp]art)\]?( |)(?P<volumeNumber>\d{1,2}|[A-H]|(IX|IV|V?I{0,3}))"
        match = re.search(volumePattern, title)
        volume = None
        if match is not None:
            volume = cls.VOLUME_LOOKUP.lookup(match.group("volumeNumber") + '.')  # adding dot as workaround to be able to use the ordinal parser
        return volume

    @classmethod
    def _hasProceeding(cls, title:str):
        return cls._titleContains("proceeding", title)

    @classmethod
    def _hasEventType(cls, title:str):
        return cls._titleContains("conference", title)

    @classmethod
    def _titleContains(cls, value:str, title:str):
        return 1.0 if title is not None and value in title.lower() else 0.0

    @classmethod
    def _countSpecialCharacters(cls, title:str):
        res = sum([1 for char in title if not(char.isalpha() or char.isdigit() or ' ')])
        return res
