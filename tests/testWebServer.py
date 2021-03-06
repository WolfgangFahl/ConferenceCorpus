'''
Created on 13.12.2021

@author: wf
'''
import unittest
from tests.datasourcetoolbox import DataSourceTest
import warnings
from corpus.web.webserver import WebServer
from corpus.web.scholar import Scholar
import json


class TestWebServer(DataSourceTest):
    """Test the WebServers RESTful interface"""
    
    def setUp(self, debug:bool=False, profile:bool=True, **kwargs) -> None:
        DataSourceTest.setUp(self, debug=debug, profile=profile, **kwargs)
        self.ws,self.app, self.client=TestWebServer.getApp()
        pass
    
    @staticmethod
    def getApp():
        warnings.simplefilter("ignore", ResourceWarning)
        ws=WebServer()
        app=ws.app
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        #hostname=socket.getfqdn()
        #app.config['SERVER_NAME'] = "http://"+hostname
        app.config['DEBUG'] = False
        client = app.test_client()
        return ws, app,client
    
    def getResponse(self,query:str):
        '''
        get a response from the app for the given query string
        
        Args:
            query(str): the html query string to fetch the response for
        '''
        response=self.client.get(query)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data is not None)
        html = response.get_data(as_text=True)
        if self.debug:
            print(html)
        return html

    def getJsonResponse(self, query: str):
        """
        get a response from the app for the given query string

        Args:
            query(str): the html query string to fetch the response for
        """
        response = self.client.get(query)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json is not None)
        return response.get_json()

    def testWebServerHome(self):
        '''
        test the home page of the Webserver
        '''
        html=self.getResponse("/")
        self.assertTrue("https://github.com/WolfgangFahl/ConferenceCorpus" in html)
        pass
        
    def testScholarCompletion(self):
        """
        tests the completion of an scholar over wikidata
        """
        expectedScholars=Scholar.getSamples()
        _ws, _app, client=self.getApp()
        data=[{"wikiDataId":"Q54303353"}]
        res=client.post('/scholar/complete', data=json.dumps(data))
        self.assertDictEqual(expectedScholars[0], res.json[0])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()