"""
Created on 19.11.2023

@author: wf
"""
from corpus.web.cc_webserver import ConferenceCorpusWebserver
from corpus.web.cc_cmd import WebserverCmd
from ngwidgets.webserver_test import WebserverTest
import json

class RestFulApiTest(WebserverTest):
    """
    test the conference corpus RESTFul APIs
    """
    
    def setUp(self, debug=False, profile=True):
        cmd_class=WebserverCmd
        server_class=ConferenceCorpusWebserver
        WebserverTest.setUp(self, server_class, cmd_class, debug=debug, profile=profile)
        
    def test_event_series_api(self):
        """
        Test getting event series information from the API.

        This test method sends a GET request to the `/eventseries/{name}` endpoint
        to retrieve data about a specific event series. The test verifies that the
        response is a valid JSON object and checks its structure and contents as needed.

        The specific event series tested here is identified by the acronym "AISI".
        See: https://github.com/WolfgangFahl/ConferenceCorpus/issues/59
        """
        test_series=[
            ("AISI",['confref', 'gnd', 'wikicfp', 'tibkat', 'wikidata'],21)
        ]
        debug=self.debug
        #debug=True
        for name,expected_sources,expected_event_count in test_series:
            path = f"/eventseries/{name}"
            json_dict = self.get_json(path)
            json_str=json.dumps(json_dict,indent=2,default=str)
            sources=list(json_dict.keys())
            event_count=0
            if debug:
                print("JSON Response:\n", json_str)
                print(f"Sources: {sources}")
            for source,events in json_dict.items():
                if debug:
                    print(f"    {source}:{len(events)}")
                event_count+=len(events)
            if debug:
                print(f"Event Count: {event_count}")
            self.assertEquals(expected_sources,sources)
            self.assertTrue(expected_event_count<=event_count)