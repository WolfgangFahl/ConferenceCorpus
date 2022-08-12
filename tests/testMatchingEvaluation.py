"""
created at 2022-08-08
updated at 2022-08-08
@author: th
"""
import json
import pathlib
import random
import unittest
import requests

from tests.basetest import BaseTest
from corpus.matching.evaluation import CM, MatchEvaluation


class TestMatching(BaseTest):
    """
    tests the matching evaluation methods
    """

    def setUp(self, debug=False, profile=True) -> None:
        """
        setup training data
        """
        super().setUp(debug, profile)
        self.acisp1996 = {
            "openresearchId": ["ACISP 1996"],
            "wikidataId": ["Q106067066"],
            "dblpConferenceId": ["conf/acisp/1996"],
            "dblpSeriesId": ["conf/acisp"],
            "gndId": ["2159559-8"],
            "seriesWikidataId": ["Q105695401"],
            "seriesWikicfpId": ["32"],
            "seriesOpenresearchId": ["ACISP"],
            "confrefId": ["acisp1996"],
            "confrefSeriesId": ["acisp"]
        }
        self.acisp1997 = {
            "openresearchId": ["ACISP 1997"],
            "wikidataId": ["Q106067060"],
            "TibKatId": ["534995004"],
            "dblpConferenceId": ["conf/acisp/1997"],
            "dblpSeriesId": ["conf/acisp"],
            "gndId": ["2164018-X"],
            "seriesWikidataId": ["Q105695401"],
            "seriesWikicfpId": ["32"],
            "seriesOpenresearchId": ["ACISP"],
            "confrefId": ["acisp1997"],
            "confrefSeriesId": ["acisp"]
        }
        self.training_data = self.load_training_data()
        self.showPlot = not self.inPublicCI()
        self.lut = {}
        # construct lookup table for source ids
        for source_id in MatchEvaluation.source_ids:
            self.lut[source_id] = {}
            for record in self.training_data.values():
                values = record.get(source_id)
                if values is None or values == []:
                    continue
                for value in values:
                    self.lut[source_id][value] = record

    @unittest.skipIf(BaseTest.inPublicCI(), "Accesses api of bitplan conferenceCorpus api → unreliable for CI")
    def test_raw_records(self):
        """
        tests existing ids directly from records
        """
        records = []
        for acronym in ["AAAI", "ACII", "ACISP"]:
            resp = requests.get(f"https://cc.bitplan.com/eventseries/{acronym}")
            for values in resp.json().values():
                records.extend(values)
        evaluation = MatchEvaluation(self.lut)
        evaluation.evaluate_records(records)
        evaluation.plot_confusion_matrix(show=self.showPlot)
        evaluation.print_scores()

    @unittest.skipIf(BaseTest.inPublicCI(), "Accesses api of bitplan conferenceCorpus api → unreliable for CI")
    def test_raw_records_reduced_evaluation(self):
        """
        tests existing ids directly from records abd reduce evaluated ids to
        """
        records = []
        for acronym in ["AAAI", "ACII", "ACISP"]:
            resp = requests.get(f"https://cc.bitplan.com/eventseries/{acronym}")
            for source, values in resp.json().items():
                if source in ["wikidata"]:
                    records.extend(values)
        print(len(records), "records")
        # for record in records:
        #     print(record)
        evaluation = MatchEvaluation(self.lut)
        evaluation.evaluate_records(records, source_id_names=["wikidataId", "seriesWikidataId", "wikicfpId"])
        evaluation.plot_confusion_matrix(show=self.showPlot)
        evaluation.print_scores()
        evaluation.plot_matching_result(classifications=[CM.TruePositive, CM.TrueNegative, CM.FalseNegative])

    def test_baseline(self):
        """
        tests evaluation by randomly generating matches
        """
        ids = []
        ids.extend([(k, v[0]) for k, v in self.acisp1996.items()])
        ids.extend([(k, v[0]) for k, v in self.acisp1997.items()])
        matches = []
        for i in range(30):
            pair = random.choices(ids, k=2)
            matches.append({
                pair[0][0]: pair[0][1],
                pair[1][0]: pair[1][1]
            })
        evaluation = MatchEvaluation(self.lut)
        evaluation.evaluate_records(matches)
        evaluation.plot_confusion_matrix(show=self.showPlot)
        evaluation.print_scores()
        evaluation.plot_matching_result(classifications=[CM.TruePositive, CM.TrueNegative, CM.FalseNegative])

    def test_perfect_match(self):
        """
        tests matching evaluation for perfect match
        """
        evaluation = MatchEvaluation(self.lut)
        record1 = {k: v[0] for k, v in self.acisp1997.items()}
        record2 = {k: v[0] for k, v in self.acisp1996.items()}
        evaluation.evaluate_records([record1, record2])
        evaluation.plot_confusion_matrix(show=self.showPlot)
        evaluation.print_scores()
        self.assertEqual(1.0, evaluation.recall)
        self.assertEqual(1.0, evaluation.precision)
        self.assertEqual(1.0, evaluation.accuracy)

    def test_match_example(self):
        """
        tests matching evaluation for perfect match
        """
        evaluation = MatchEvaluation(self.lut)
        record1 = {
            "openresearchId": "ACISP 1997",
            "wikidataId": "Q106067066",
            "dblpConferenceId": "conf/acisp/1996",
            "dblpSeriesId": "conf/acisp",
            "gndId": "2159559-8",
            "seriesWikidataId": "Q105695401",
            "seriesWikicfpId": "32",
            "seriesOpenresearchId": "ACISP",
            "confrefId": "acisp1996",
            "confrefSeriesId": "acisp"
        }
        evaluation.evaluate_records([record1], source_id_names=["wikidataId", "openresearchId", "dblpConferenceId"])
        evaluation.plot_confusion_matrix(show=self.showPlot)
        evaluation.print_scores()
        evaluation.plot_matching_result(classifications=[CM.TruePositive, CM.TrueNegative, CM.FalseNegative])

    def test_checkMatch(self):
        """
        tests checkMatch
        """
        evaluation = MatchEvaluation(self.lut)

        # test valid matches
        for record in [self.acisp1996, self.acisp1997]:
            for source1, id1 in record.items():
                for source2, id2 in record.items():
                    is_valid_match = evaluation.check_matching(source1, str(id1[0]), source2, str(id2[0]))
                    self.assertTrue(is_valid_match, f"{id1} !→ {id2}")
        # test invalid matches
        for source1, id1 in self.acisp1996.items():
            for source2, id2 in self.acisp1997.items():
                if "series" in source1.lower() or "series" in source2.lower():
                    continue
                is_valid_match = evaluation.check_matching(source1, str(id1[0]), source2, str(id2[0]))
                self.assertFalse(is_valid_match)

    def test_group_ids_by_source(self):
        """
        tests group_ids_by_source
        """
        lod = [
            {"openresearchId": "AAAI 2020", "confrefId": "aaai2020"},
            {"openresearchId": "AAAI 2019", "confrefId": "aaai2019"},
        ]
        me = MatchEvaluation(self.lut)
        res = me.group_ids_by_source(lod)
        expected = {
            "openresearchId": ["AAAI 2020", "AAAI 2019"],
            "confrefId": ["aaai2020", "aaai2019"]
        }
        for sourceIdName, ids in expected.items():
            self.assertIn(sourceIdName, res)
            for sourceId in ids:
                self.assertIn(sourceId, res.get(sourceIdName, []))

    def test_convert_to_labeled_matching_result(self):
        """
        tests convert_to_labeled_matching_result
        """
        self.assertEqual([], MatchEvaluation.convert_to_labeled_matching_result([]))
        self.assertEqual("match", MatchEvaluation.convert_to_labeled_matching_result([True])[0])
        self.assertEqual("no-match", MatchEvaluation.convert_to_labeled_matching_result([False])[0])
        data = [True, False, False, True, False]
        expected = ["match", "no-match", "no-match", "match","no-match"]
        res = MatchEvaluation.convert_to_labeled_matching_result(data)
        self.assertEqual(len(expected), len(res))
        for i, value in enumerate(expected):
            self.assertEqual(value, res[i])

    @staticmethod
    def load_training_data() -> dict:
        """
        loads the training data set
        """
        grandParent = pathlib.Path(__file__).parent.parent.resolve()
        filepath = (grandParent / "resources/matching/training_set.json")
        path = str(filepath)
        with open(path, mode="r") as fp:
            lod = json.load(fp)
        return lod
