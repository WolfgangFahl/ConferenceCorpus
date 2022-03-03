import sys
from tempfile import NamedTemporaryFile

from wikifile.wikiFile import WikiFile

from corpus.datasources.tibkat import Tibkat, main
from tests.datasourcetoolbox import DataSourceTest
from tests.testSMW import TestSMW


class TestTibkat(DataSourceTest):
    """
    tests Tibkat
    """

    def setUp(self,debug=False,profile=True):
        super().setUp(debug=debug, profile=profile)
        self.testWikiId = getattr(TestSMW.getWikiUser("orfixed"), "wikiId")

    def test_TibkatCommandline(self):
        """
        test the tibkat commandline
            - parsing of the json from stdin
            - updating of corresponding events in the wiki
        """
        if self.inCI():
            return
        data="""[]
[
  {
    "title": "Affective computing and intelligent interaction : 4th international conference, ACII 2011, Memphis, TN, USA, October 9-12, 2011; proceedings / Sidney DḾello ... (eds.) ; Pt. 2",
    "event": "ACII ; 4",
    "desc": "ACII ; 4 (Memphis, Tenn.) : 2011.10.09-12",
    "starttime": "2011-10-09",
    "endtime": "2011-10-12",
    "location": "Memphis, Tenn.",
    "ppn": "668314257",
    "isbn13": "9783642245701",
    "firstid": "DNB:1014976871"
  },
  {
    "title": "Affective computing and intelligent interaction : 4th international conference, ACII 2011, Memphis, TN, USA, October 9-12, 2011; proceedings / Sidney DḾello ... (eds.) ; Pt. 2",
    "event": "International Conference of the Humaine Association on Affective Computing and Intelligent Interaction ; 4",
    "desc": "International Conference of the Humaine Association on Affective Computing and Intelligent Interaction ; 4 (Memphis, Tenn.) : 2011.10.09-12",
    "starttime": "2011-10-09",
    "endtime": "2011-10-12",
    "location": "Memphis, Tenn.",
    "ppn": "668314257",
    "isbn13": "9783642245701",
    "firstid": "DNB:1014976871"
  },
  {
    "title": "Affective computing and intelligent interaction : 4th international conference, ACII 2011, Memphis, TN, USA, October 9-12, 2011; proceedings / Sidney DḾello ... (eds.) ; Pt. 1",
    "event": "ACII ; 4",
    "desc": "ACII ; 4 (Memphis, Tenn.) : 2011.10.09-12",
    "starttime": "2011-10-09",
    "endtime": "2011-10-12",
    "location": "Memphis, Tenn.",
    "ppn": "668314389",
    "isbn13": "9783642245992",
    "firstid": "DNB:1014977010"
  }
]
[
  {
    "title": "2015 International Conference on Affective Computing and Intelligent Interaction (ACII) : 21 - 24 Sept. 2015, Xi'an",
    "event": "ACII ; 6",
    "desc": "ACII ; 6 (Xi'an, China) : 2015.09.21-24",
    "starttime": "2015-09-21",
    "endtime": "2015-09-24",
    "location": "Xi'an, China",
    "ppn": "843967234",
    "isbn13": "9781479999538",
    "firstid": "GBV:843967234"
  }
]
        """
        with NamedTemporaryFile() as fp:
            fp.write(data.encode())
            fp.seek(0)
            args = ["-t", self.testWikiId, "-f", fp.name]
            main(args)

    def test_addPpnIdToWiki(self):
        """
        tests adding a ppn to an existing event is the wiki
        """
        if self.inCI():
            return
        record = {
            "event": "AAAI ; 1",
            "ppn": "02205460X"
        }
        tibkat = Tibkat()
        tibkat.addPpnIdToWiki(self.testWikiId, record)

    def test_getMatchingEventFromWiki(self):
        """
        tests the retrieval of event pages based on the series acronym and ordinal
        """
        if self.inCI():
            return
        tibkat = Tibkat()
        res = tibkat.getMatchingEventFromWiki(self.testWikiId, "AAAI", 1)
        self.assertIsInstance(res, WikiFile)
        self.assertEqual("AAAI 1980", res.getPageTitle())