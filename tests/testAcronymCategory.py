import os
import re
from typing import List

import yaml
from ptp.parsing import Tokenizer

from corpus.event import EventStorage
from corpus.eventcorpus import DataSource
from corpus.utils.plots import PlotSettings, Histogramm
from ptp.signature import EnumCategory, OrdinalCategory, YearCategory, AcronymCategory
from tests.basetest import BaseTest


class TestAcronymCategory(BaseTest):
    """
    tests AcronymCategory
    """

    def setUp(self,debug=False,profile=True):
        super().setUp(debug, profile)
        self.histroot = "/tmp/histogramms"
        os.makedirs(self.histroot, exist_ok=True)

    def testAcronymCategory(self):
        """
        tests tokenization of cities with the CityCategory
        """
        tokenizer = Tokenizer([AcronymCategory()])
        testParams = [
            ("AAAI", "Proceedings of the Twenty-Third AAAI Conference on Artificial Intelligence and the Twentieth Innovative Applications of Artificial Intelligence Conference : 13-17 July 2008, Chicago, Illinois, USA ; Vol. 2"),
            ("NEMS", "12th International Conference on Nano/Micro Engineered and Molecular Systems, NEMS 2017, Los Angeles, CA, USA, April 9-12, 2017"),
            ("LANOMS", "1st Latin American Network Operations and Management Symposium, LANOMS 1999, Rio de Janeiro, Brazil, December 3-5, 1999"),
            (None,"1960 proceedings of Instrument Society of America 15th Annual Instrument-Automation Conference and Exhibit, New York City, New York, September 26 - 30, 1960 ; Pt. 2")
        ]
        for expectedValue, title in testParams:
            tokenSequence = tokenizer.tokenize(title, f"test_for_{expectedValue}")
            matches = tokenSequence.getTokenOfCategory("acronym")
            if expectedValue is None:
                self.assertEqual(0, len(matches))
            else:
                self.assertEqual(1, len(matches))
                self.assertEqual(expectedValue, matches[0].value)

    def testAcronymDistribution(self):
        """
        tests acronym distribution
        """

        def histogrammSettings(plot):
            pass

        for source in list(DataSource.getDatasources()):
            if source.name in ["acm", "ceurws", "or", "orbackup", "orclonebackup"]:
                continue
            with self.subTest(source=source):
                sqlQuery = f"""SELECT acronym FROM {source.tableName} WHERE acronym IS NOT NULL"""
                sqlDB = EventStorage.getSqlDB()
                lod = sqlDB.query(sqlQuery)
                acronyms = [d.get("acronym") for d in lod]

                # acronym length distribution
                values = list((len(acronym) for acronym in acronyms))
                histOutputFileName = f"acronymLengthDistro_{source.name}"
                h = Histogramm(x=values)
                hps = PlotSettings(outputFile=f"{self.histroot}/{histOutputFileName}.png", callback=histogrammSettings)
                h.show(xLabel='acronym length',
                       yLabel='distribution',
                       title=f'Acronym length distribution of data source {source.name}',
                       density=True,
                       ps=hps)

                # acronym structure
                histOutputFileName = f"acronymBlanksDistro_{source.name}"
                values = list((acronym.strip().count(" ") for acronym in acronyms))
                h2 = Histogramm(x=values)
                hps = PlotSettings(outputFile=f"{self.histroot}/{histOutputFileName}.png", callback=histogrammSettings)
                h2.show(xLabel='number of blanks in acronym',
                       yLabel='distribution',
                       title=f'Distribution of number of blanks in acronyms in the data source {source.name}',
                       density=True,
                       ps=hps)

                # length distribution of first word of two word acronyms
                values = list((len(acronym.split(" ")[0].strip(" ()#")) for acronym in acronyms if acronym.count(" ") <= 1))
                histOutputFileName = f"acronymFirstWordLengthDistro_{source.name}"
                h = Histogramm(x=values)
                hps = PlotSettings(outputFile=f"{self.histroot}/{histOutputFileName}.png", callback=histogrammSettings)
                h.show(xLabel='length of first word',
                       yLabel='distribution',
                       title=f'Length distribution of the first word of acronyms of data source {source.name}',
                       density=True,
                       ps=hps)

                #distribution of capital letters
                values = list((acronym.split(" ")[0].strip(" ()#") for acronym in acronyms if acronym.count(" ") <= 1))
                values = [sum(map(str.isupper, v)) for v in values]
                histOutputFileName = f"acronymCapitalLettersDistro_{source.name}"
                h = Histogramm(x=values)
                hps = PlotSettings(outputFile=f"{self.histroot}/{histOutputFileName}.png", callback=histogrammSettings)
                h.show(xLabel='number of capital letters in first word',
                       yLabel='distribution',
                       title=f'Distribution of capital letters in the first word of acronyms of data source {source.name}',
                       density=True,
                       ps=hps)


    def testGenerateAcronymYaml(self):
        """
        generates the prefix yaml for city names
        """
        ordinalMatcher = OrdinalCategory()
        yearMatcher = YearCategory()
        acronyms = self.getAcronyms(["tibkat", "gnd", "dblp", "acm"])
        coLocatedAcronyms = [acronym for acronym in acronyms if "@" in acronym]
        acronyms = [acronym
                    for acronym in acronyms
                    if "@" not in acronym]
        for coLocatedAcronym in coLocatedAcronyms:
            acronyms.extend(coLocatedAcronym.split("@"))
        acronyms = list(set(acronyms))
        acronyms = [acronym.split(" ")[0].strip(" ()#")
                    for acronym in acronyms
                    if acronym.count(" ") <= 1]
        acronyms = [acronym
                    for acronym in acronyms
                    if  2 < len(acronym) <= 10
                    and sum(map(str.isupper, acronym)) > 1
                    and not ordinalMatcher.checkMatch(acronym)
                    and not yearMatcher.checkMatch(acronym)]
        print("Number of distinct acronyms", len(acronyms))
        acronymYaml = {
            acronym: {
                "type": "acronym",
                "value": acronym
            }
            for acronym in acronyms
        }
        with open("/tmp/acronyms.yaml", mode="w") as fp:
            desc = """#\n# Acronyms of events\n#\n"""
            fp.write(desc)
            yaml.dump(acronymYaml, fp)

    def getAcronyms(self, excludeSources:list = None) -> List[str]:
        """
        Get all event titles of the given source
        Args:
            source: name of the data source

        Returns:
            all titles of the given data source
        """
        sqlQuery = f"""SELECT DISTINCT acronym FROM event WHERE acronym IS NOT NULL"""
        if excludeSources is not None:
            for source in excludeSources:
                sqlQuery += f" AND source != '{source}' "
        sqlDB = EventStorage.getSqlDB()
        lod = sqlDB.query(sqlQuery)
        acronyms = [d.get('acronym') for d in lod]
        return acronyms