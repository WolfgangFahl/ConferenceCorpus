from ptp.parsing import Tokenizer
from pyparsing.diagram import to_railroad, railroad_to_html

from ptp.eventrefparser import EventReferenceParser
from ptp.signature import VolumeCategory
from tests.basetest import BaseTest


class TestVolumeCategory(BaseTest):
    """
    tests VolumeCategory
    """

    def testMatching(self):
        """
        tests matching the label
        """
        labels = ["volume", "vol.", "part", "pt."]
        values = [('1',1), ('2',2), ('3',3), ('A',1), ('B',2), ('C',3), ('I',1), ('II',2), ('III',3), ('IV',4), ('V',5)]
        category = VolumeCategory()
        for label in labels:
            for value, expectedVolume in values:
                volumeStr = f"{label} {value}"
                matchedVolume = category.getValue(volumeStr)
                self.assertEqual(expectedVolume, matchedVolume, f"Expected volume {expectedVolume} from '{volumeStr}'")

    def testPlotVolumeParser(self):
        return
        with open('/tmp/volumeCategoryParser.html', 'w') as fp:
            railroad = to_railroad(VolumeCategory.VOLUME, show_results_names=True, show_groups=False)
            print(str(railroad))
            fp.write(railroad_to_html(railroad))

    def testVolumeCategory(self):
        """
        tests tokenization of volume category
        """
        tokenizer = Tokenizer([VolumeCategory()])
        event = {
            'acronym': 'AAAI 23',
            'title': 'Proceedings of the Twenty-Third AAAI Conference on Artificial Intelligence and the Twentieth Innovative Applications of Artificial Intelligence Conference : 13-17 July 2008, Chicago, Illinois, USA ; Vol. 2'
        }
        tokenSequence = tokenizer.tokenize(event['title'], event)
        self.assertEqual(2, len(tokenSequence.matchResults))
        for token in tokenSequence.matchResults:
            self.assertEqual('volume', token.category.name)
            self.assertIn(token.value, ["LABEL", 2])
            if token.value == "LABEL":
                self.assertEqual(26, token.pos)
            else:
                self.assertEqual(27, token.pos)
                self.assertEqual(2, token.value)