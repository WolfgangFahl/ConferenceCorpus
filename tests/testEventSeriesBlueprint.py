from dataclasses import asdict

from spreadsheet.googlesheet import GoogleSheet

from corpus.web.eventseries import MetadataMappings
from tests.basetest import BaseTest

class TestEventSeriesBlueprint(BaseTest):
    """
    tests EventSeriesBlueprint
    """


    def test_extractWikidataMapping(self):
        """
        extracts wikidata metadata mapping from given google docs url
        """
        return
        url = ""
        gs = GoogleSheet(url)
        gs.open(["Wikidata"])
        sheet = [{k:v for k,v in record.items() if (not k.startswith("Unnamed")) and v is not ''} for record in gs.asListOfDicts("Wikidata")]
        print(sheet)

    def test_MetadataMapping(self):
        mapping = MetadataMappings()
        print(asdict(mapping))