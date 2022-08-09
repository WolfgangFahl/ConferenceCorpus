"""
created at 2022-08-08
updated at 2022-08-08
@author: th
"""

import itertools
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
from sklearn import metrics
from sklearn.metrics import precision_score, recall_score, accuracy_score


class MatchEvaluation:
    """
    provides method to analyze event matchings
    """
    source_ids = ['openresearchId', 'wikicfpId', 'wikidataId', 'TibKatId', 'dblpConferenceId', 'dblpSeriesId',
                  'gndId', 'seriesWikidataId', 'seriesWikicfpId', 'seriesOpenresearchId', 'confrefId',
                  'confrefSeriesId']

    def __init__(self, training_data: Dict[str, Dict[str, List[str]]]):
        """
        constructor

        Args:
            training_data: for every source an id lookup for the matches to other sources
        """
        self.lut = training_data
        self.evaluation_result: List[Tuple[bool, bool]] = []

    @property
    def actual(self):
        """
        Ground truth (correct) target values
        """
        return [actual for actual, _ in self.evaluation_result]

    @property
    def predicted(self):
        """
        Estimated targets (True if match is valid)
        """
        return [predicted for _, predicted in self.evaluation_result]

    @property
    def precision(self) -> float:
        """
        Compute the precision.
        """
        return precision_score(self.actual, self.predicted)

    @property
    def recall(self) -> float:
        """
        Compute the recall.
        """
        return recall_score(self.actual, self.predicted)

    @property
    def accuracy(self) -> float:
        """
        Accuracy classification score.
        """
        return accuracy_score(self.actual, self.predicted)

    def print_scores(self):
        """
        prints the evaluation scores
        """

        print('Precision: %.3f' % self.precision)
        print('Recall: %.3f' % self.recall)
        print('Accuracy: %.3f' % self.accuracy)

    @staticmethod
    def convert_to_labeled_matching_result(result: List[bool]):
        """
        converts the given matching results to a labeled list
        """
        return ["match" if match else "no-match" for match in result]

    def plot_confusion_matrix(self, show: bool=False):
        """
        prints out different evaluation metrics
        """
        y_true = self.convert_to_labeled_matching_result(self.actual)
        pred = self.convert_to_labeled_matching_result(self.predicted)
        metrics.ConfusionMatrixDisplay.from_predictions(y_true, pred)
        plt.xlabel('Prediction', fontsize=18)
        plt.ylabel('Actual', fontsize=18)
        plt.title('Confusion Matrix', fontsize=18)
        if show:
            plt.show()

    def evaluate_records(self, records: List[dict]):
        """
        evaluates the given records and checks id the matchings are correct
        Args:
            records: list of event records
        """
        self.normalize_records(records)
        id_lut = self.group_ids_by_source(records)
        for record in records:
            for source_id_1, source_id_2 in itertools.product(self.source_ids, self.source_ids):
                v1_ids = record.get(source_id_1, [])
                v2_ids = record.get(source_id_2, [])
                if v1_ids is None:
                    v1_ids = []
                if v2_ids is None:
                    v2_ids = []
                if isinstance(v1_ids, str):
                    v1_ids = v1_ids.split("⇹")
                if isinstance(v2_ids, str) and v2_ids is not None:
                    v2_ids = v2_ids.split("⇹")
                if source_id_1 == source_id_2:
                    continue
                # check present matches
                for v1, v2 in itertools.product(v1_ids, v2_ids):
                    if v1 is not None and v2 is not None:
                        expected = True
                        actual = self.check_matching(source_id_1, v1, source_id_2, v2)
                        self.evaluation_result.append((actual, expected))
                if "series" in source_id_1.lower():
                    # series is only checked from the other direction
                    continue
                # check for missing matches
                for no_match_ids in id_lut[source_id_2].difference(v2_ids):
                    expected = False
                    for v1 in v1_ids:
                        actual = self.check_matching(source_id_1, v1, source_id_2, no_match_ids)
                        self.evaluation_result.append((actual, expected))

    def check_matching(self, source1: str, id1: str, source2: str, id2: str):
        """
        Check if the given matching is correct
        Args:
            source1: source id name
            id1: id value of the first source
            source2: source id name
            id2: id value of the second source

        Returns:
            True if the given matching is correct. Otherwise, False is returned.
        """
        try:
            valid_match = id2 in self.lut.get(source1, {}).get(id1, {}).get(source2,  [])
            valid_match = valid_match or id1 in self.lut.get(source2, {}).get(id2, {}).get(source1, [])
        except Exception:
            valid_match = False
        return valid_match

    @staticmethod
    def normalize_records(records: List[dict]):
        """
        normalizes the source id property names
        Args:
            records: list of event records
        """
        for record in records:
            source = record.get("source")
            event_id = record.get("eventId")
            series_id = record.get("seriesId")
            if source == "confref":
                record['confrefId'] = event_id
                record['confrefSeriesId'] = series_id
            elif source == "dblp":
                record["dblpConferenceId"] = event_id
                if series_id is not None:
                    record["dblpSeriesId"] = "conf/" + series_id
            elif source == "tibkat":
                record["TibKatId"] = event_id
                record["gndId"] = record.get("gndIds")
            elif source == "wikicfp":
                record["wikicfpId"] = event_id
                record["seriesWikicfpId"] = series_id
            elif source == "wikidata":
                record["wikidataId"] = event_id
                record["seriesWikidataId"] = record.get("eventInSeriesId")
                record["dblpConferenceId"] = record.get("dblpId")
                record["wikicfpId"] = record.get("wikiCfpId")
            elif source in ["orclone", "openresearch"]:
                record["openresearchId"] = event_id
                record["seriesOpenresearchId"] = record.get("inEventSeries")
                dblp_conference_id = record.get("dblpId")
                if dblp_conference_id is not None and not dblp_conference_id.startswith("conf/"):
                    dblp_conference_id = "conf/" + dblp_conference_id
                record["dblpConferenceId"] = dblp_conference_id

    def group_ids_by_source(self, records: List[dict]) -> Dict[str, set]:
        """
        for each source id in self.sourceIds provide a set of all used Ids
        Args:
            records: list of event records

        Returns:
            Returns for each sourceId the set of all used ids
        """
        res = {}
        for sourceId in self.source_ids:
            ids = {record.get(sourceId) for record in records if record.get(sourceId) is not None}
            res[sourceId] = ids
        return res
