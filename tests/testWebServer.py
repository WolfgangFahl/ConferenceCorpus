'''
Created on 13.12.2021

@author: wf
'''
import unittest
import json
from tests.datasourcetoolbox import DataSourceTest
import warnings
from corpus.web.webserver import WebServer

class TestWebServer(DataSourceTest):
    """Test the WebServers RESTful interface"""
    
    def setUp(self) -> None:
        DataSourceTest.setUp(self)
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
        html=response.data.decode()
        if self.debug:
            print(html)
        return html 

    def testWebServerHome(self):
        '''
        test the home page of the Webserver
        '''
        html=self.getResponse("/")
        self.assertTrue("https://github.com/WolfgangFahl/ConferenceCorpus" in html)
        pass
    
    def testGetEventSeries(self):
        '''
        tests the multiquerying of event series over api
        
        some 17 secs for test
        '''
        jsonStr=self.getResponse("/eventseries/WEBIST?format=json")
        res=json.loads(jsonStr)
        print(res)
        self.assertTrue("confref" in res)
        self.assertTrue(len(res["confref"])>15)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()