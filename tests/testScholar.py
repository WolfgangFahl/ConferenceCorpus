import json

from corpus.web.scholar import Scholar
from tests.testWebServer import TestWebServer


class TestScholarBlueprint(TestWebServer):
    """
    test ScholarBlueprint
    """

    def testScholarCompletion(self):
        """
        tests the completion of an scholar over wikidata
        """
        expectedScholars=Scholar.getSamples()
        ws, app, client=self.getApp()
        data=[{"wikiDataId":"Q54303353"}]
        res=client.post('/scholar/complete', data=json.dumps(data))
        self.assertDictEqual(expectedScholars[0], res.json[0])