'''
Created on 2022-04-03

@author: wf
'''
from typing import List, Tuple


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
    def getCompletedBlankSeries(cls, lod:dict, debug:bool=False) -> list:
        """
        gets all blank entries of a series from the different records that are given.
        It is expected that each lod comes from a  different datasource
        Args:
            lods:

        Returns:
            List of completed year ordinal pairs, or empty list if given lod can not be completed
        """
        yearOrdinalPair = {(r.get('year'), r.get("ordinal")) for r in lod }
        completeYearOrdinalPair = list({(year, ordinal) for year, ordinal in yearOrdinalPair if year is not None and ordinal is not None})
        completeYearOrdinalPair.sort(key=lambda r: r[0] if r[0] is not None else 0)
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
