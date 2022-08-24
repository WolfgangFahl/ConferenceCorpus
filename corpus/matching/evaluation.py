"""
created at 2022-08-08
updated at 2022-08-08
@author: th
"""

import itertools
import json
import pathlib
from enum import Enum

import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
from sklearn import metrics
from sklearn.metrics import precision_score, recall_score, accuracy_score
from dataclasses import dataclass

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
        self.results: List[MatchingResult] = []

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

    def get_results_classified_as(self, classifications: List['CM']) -> List['MatchingResult']:
        """

        Args:
            classifications: result classifications that should be printed out

        Returns:
            list of matching results
        """
        res = [mr for mr in self.results if mr.classification in classifications]
        return res

    def plot_matching_result(self, classifications: List['CM'] = None):
        """
        generates a graphviz plot of the matching result
        Args:
            classifications: result classifications that should be included in the plot

        Returns:

        """
        results = self.results
        if classifications is not None:
            results = self.get_results_classified_as(classifications)
        plot_body = ""
        id_lut = {}
        for result in results:
            id_lut[result.id_1] = (result.id_1.__hash__(), result.source_1)
            id_lut[result.id_2] = (result.id_2.__hash__(), result.source_2)
        # add all nodes
        for label, (node_name, source) in id_lut.items():
            plot_body += f"""{node_name} [label="{label}"]\n"""  # ToDo: add color
        for result in results:
            color = ""
            if result.classification == CM.FalseNegative:
                color = "orange"
            elif result.classification == CM.TrueNegative:
                color = "red"
            else:
                color = "green"
            relation_att = f"""[ color="{color}"]"""
            plot_body += f"""{id_lut[result.id_1][0]} -- {id_lut[result.id_2][0]} {relation_att};\n"""
        legend = f"""subgraph cluster_01 {{
    label = "Legend";
    node [shape=point]
    {{
        rank=same
        d0 [style = invis];
        d1 [style = invis];
        p0 [style = invis];
        p1 [style = invis];
        s0 [style = invis];
        s1 [style = invis];
    }}
    d0 -- d1 [label=correct color=green]
    p0 -- p1 [label="incorrect/\nnot in source of truth" color=red]
    s0 -- s1 [label=missing color=orange]
}}"""
        plot = f"""graph untitl {{\n rankdir=LR;\n {plot_body}\n{legend}\n}}"""
        with open("/tmp/matching_result.txt", mode="w") as fp:
            print(plot, file=fp)


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
        metrics.ConfusionMatrixDisplay.from_predictions(y_true, pred, cmap=plt.cm.Blues)
        plt.xlabel('Prediction', fontsize=18)
        plt.ylabel('Actual', fontsize=18)
        plt.title('Confusion Matrix', fontsize=18)
        if show:
            plt.show()

    def evaluate_records(self, records: List[dict], source_id_names: List[str] = None):
        """
        evaluates the given records and checks id the matchings are correct
        Args:
            records: list of event records
            source_id_names: names of the source ids which should be evaluated. the names must be included in the source_ids
        """
        if source_id_names is None:
            source_id_names = self.source_ids
        self.normalize_records(records)
        id_lut = {k: set(v.keys()) for k, v in self.lut.items()}
        for record in records:
            for i, source_id_1 in enumerate(source_id_names):
                for source_id_2 in source_id_names[i:]:
                    v1_ids = self.get_ids_from_record(record, source_id_1)
                    v2_ids = self.get_ids_from_record(record, source_id_2)
                    if source_id_1 == source_id_2:
                        continue
                    # check present matches
                    for v1, v2 in itertools.product(v1_ids, v2_ids):
                        if v1 is not None and v2 is not None:
                            expected = True
                            actual = self.check_matching(source_id_1, v1, source_id_2, v2)
                            if actual:
                                self.results.append(MatchingResult(CM.TruePositive, source_id_1, v1, source_id_2, v2))
                            else:
                                self.results.append(MatchingResult(CM.TrueNegative, source_id_1, v1, source_id_2, v2))
                            self.evaluation_result.append((actual, expected))
                    if "series" in source_id_1.lower():
                        # series is only checked from the other direction
                        continue
                    # check for missing matches
                    for no_match_id in id_lut[source_id_2].difference(v2_ids):
                        expected = False
                        for v1 in v1_ids:
                            actual = self.check_matching(source_id_1, v1, source_id_2, no_match_id)
                            if actual:
                                self.results.append(
                                        MatchingResult(CM.FalseNegative, source_id_1, v1, source_id_2, no_match_id))
                            else:
                                self.results.append(
                                    MatchingResult(CM.FalsePositive, source_id_1, v1, source_id_2, no_match_id))
                            self.evaluation_result.append((actual, expected))

    @staticmethod
    def get_ids_from_record(record: dict, source_id_name:str, separator: str = "⇹") -> List[str]:
        """
        extract and convert the value for the given source id property

        Args:
            record: event record
            source_id_name: name of the source id property
            separator: id separator

        Returns:
            list of ids for the given source_id_name
        """
        if separator is None:
            separator = "⇹"
        res = record.get(source_id_name, [])
        if res is None:
            res = []
        if isinstance(res, str):
            res = res.split(separator)
        return res


    def evaluate_present_matches(self, ):
        """
        evaluates explicitly stated matchings
        """
        pass

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

    def group_ids_by_source(self, records: List[dict], source_id_names: List[str] = None) -> Dict[str, set]:
        """
        for each source id in self.sourceIds provide a set of all used Ids
        Args:
            records: list of event records

        Returns:
            Returns for each sourceId the set of all used ids
        """
        if source_id_names is None:
            source_id_names = self.source_ids
        res = {}
        for sourceId in source_id_names:
            ids = set()
            for record in records:
                if record.get(sourceId) is not None:
                    value = record.get(sourceId, [])
                    if isinstance(value, list):
                        ids.union(value)
                    else:
                        ids.add(value)
            res[sourceId] = ids
        return res

    @classmethod
    def fromResources(cls) -> 'MatchEvaluation':
        """
        Load MatchEvaluation with training data from the resources
        """
        grandParent = pathlib.Path(__file__).parent.parent.parent.resolve()
        filepath = (grandParent / "resources/matching/training_set.json")
        path = str(filepath)
        with open(path, mode="r") as fp:
            lod = json.load(fp)
        lut = {}
        # construct lookup table for source ids
        for source_id in MatchEvaluation.source_ids:
            lut[source_id] = {}
            for record in lod.values():
                values = record.get(source_id)
                if values is None or values == []:
                    continue
                for value in values:
                    lut[source_id][value] = record
        matchEvaluation = MatchEvaluation(training_data=lut)
        return matchEvaluation


@dataclass
class MatchingResult:
    """
    represents a matching result
    """
    classification: 'CM'
    source_1: str
    id_1: str
    source_2: str
    id_2: str

class CM(Enum):
    """
    results of the confusion matrix
    """
    TruePositive = "TP"
    FalsePositive = "FP"
    TrueNegative = "TN"
    FalseNegative = "FN"