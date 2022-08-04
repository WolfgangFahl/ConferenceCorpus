import os
import unittest
from collections import Counter
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
from docutils.nodes import legend

from corpus.utils.plots import Histogramm, PlotSettings, HistogramSeries, Plot
from ptp.parsing import Tokenizer

from corpus.event import EventStorage
from ptp.signature import OrdinalCategory, EnumCategory, AcronymCategory
from tests.basetest import BaseTest


@unittest.skip("Under development currently a clear indication is not visible besides the obvious key words → further analysis needed")
class TestCoLocation(BaseTest):
    """
    analyzes the event titles of co-located events
    """

    def setUp(self,debug=False,profile=True):
        super().setUp(debug, profile)
        self.tokenizer = Tokenizer([OrdinalCategory(), EnumCategory('eventType'), EnumCategory('scope'), AcronymCategory()])
        self.histroot = "/tmp/histogramms"
        os.makedirs(self.histroot, exist_ok=True)

    def getTitlesOfSource(self, source:str) -> List[str]:
        """
        Get all event titles of the given source
        Args:
            source: name of the data source

        Returns:
            all titles of the given data source
        """
        sqlQuery = f"""SELECT title FROM event_{source} WHERE title IS NOT NULL"""
        sqlDB = EventStorage.getSqlDB()
        lod = sqlDB.query(sqlQuery)
        titles = [d.get('title') for d in lod]
        return titles

    def convertToDf(self, lod:List[dict], index:str=None) -> pd.DataFrame:
        df_lod = pd.DataFrame.from_records(lod, index=index)
        df_lod = df_lod.fillna(0)
        return df_lod

    def testCoLocatedEventsFeatureDistribution(self):
        """
        plots the distribution of parsed feature categories of co-located events
        """
        source = "dblp"
        titles = self.getTitlesOfSource(source)
        coLocatedLod = []
        notCoLocatedLod = []
        lod = []
        for title in titles:
            tokenSeq = self.tokenizer.tokenize(title, "testCoLocatedEventsFeatureDistribution")
            matchedCategories = [token.name for token in tokenSeq.matchResults]
            counter = Counter(matchedCategories)
            if "co-located" in title:
                coLocatedLod.append(counter)
            else:
                notCoLocatedLod.append(counter)
            lod.append(counter)
        df_lod = self.convertToDf(lod)
        df_coLocatedLod = self.convertToDf(coLocatedLod)
        df_notCoLocatedLod = self.convertToDf(notCoLocatedLod)
        for feature in ["Ordinal", "eventType", "scope", "acronym"]:
            histOutputFileName=f"coLocated{feature.title()}Matches_{source}"
            h = HistogramSeries(series={
                "co-located in title": df_coLocatedLod[feature],
                "co-located not in title": df_notCoLocatedLod[feature]
            })
            def histogramSettings(plot):
                pass
            hps = PlotSettings(outputFile=f"{self.histroot}/{histOutputFileName}.png", callback=histogramSettings)
            h.show(xLabel='number of matches',
                   yLabel='distribution',
                   title=f'number of {feature} matches in "co-located" event title ',
                   density=False,
                   alpha=0.5,
                   ps=hps, bins=10)

    def testEventTypeCombinations(self):
        """
        tests the eventType combinations
        """
        source = "dblp"
        titles = self.getTitlesOfSource(source)
        res = {}
        for title in titles:
            tokenSeq = self.tokenizer.tokenize(title, "testCoLocatedEventsFeatureDistribution")
            matchedCategories = list(set((token.value.lower() for token in tokenSeq.matchResults if token.name=="eventType")))
            matchedCategories.sort()
            category = '&'.join(matchedCategories)
            isCoLocated = "co-located" in title
            if category not in res:
                res[category] = {True:0, False:0, 'total':0}
            res[category][isCoLocated] += 1
            res[category]['total'] += 1
        lod = [{"categories":k, **v} for k, v in res.items()]
        lod.sort(key=lambda record: record.get('total',0), reverse=True)
        def histogramSettings(plot):
            pass
        histOutputFileName = f"eventTypeCombinationsCoLocation_{source}"
        ps = PlotSettings(outputFile=f"{self.histroot}/{histOutputFileName}.png", callback=histogramSettings)
        plot = Plot()
        plot.setup(title="EventType combinations in correlation with co-located events")
        df = self.convertToDf(lod, index="categories")
        df=df.drop(['total'], axis=1)
        df.plot(kind='bar', stacked=True, figsize=(20, 10), logy=False)
        plt.tight_layout()
        plot.doShow(ps)

    def testCoLocatedEventsFeatureContradiction(self):
        """
        plots the distribution of parsed feature categories of co-located events
        """
        source = "dblp"
        titles = self.getTitlesOfSource(source)
        lod = []
        for title in titles:
            tokenSeq = self.tokenizer.tokenize(title, "testCoLocatedEventsFeatureDistribution")
            ordinalTokens = tokenSeq.getTokenOfCategory("Ordinal")
            acronymTokens = tokenSeq.getTokenOfCategory("acronym")
            isCoLocated = "co-located" in title
            contradictingOrdinals = len(set(token.value for token in ordinalTokens)) > 1
            contradictingAcronyms = len(set(token.value for token in acronymTokens)) > 1
            res = {
                "isCoLocated": int(isCoLocated),
                "contradictingOrdinals": int(contradictingOrdinals),
                "contradictingAcronyms": int(contradictingAcronyms),
                "contradictingAcronyms&Ordinal": int(contradictingOrdinals and contradictingAcronyms)
            }
            if contradictingOrdinals and contradictingAcronyms:
                print(title)
            lod.append(res)
        df = self.convertToDf(lod)
        df.drop(['isCoLocated'], axis=1).hist(by=df['isCoLocated'], legend=True)
        plt.legend(loc='upper right')
        plt.show()

