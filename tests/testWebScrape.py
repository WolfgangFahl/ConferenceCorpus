'''
Created on 2021-07-31

@author: wf
'''
import unittest
from datasources.webscrape import WebScrape

class TestWebScrape(unittest.TestCase):
    '''
    test getting rdfA based triples from Webpages
    '''

    def setUp(self):
        self.debug=False
        pass


    def tearDown(self):
        pass


    def testWebScrape(self):
        '''
        test getting rdfA encoded info from a webpage
        '''
        url="http://ceur-ws.org/Vol-2635/"
        scrape=WebScrape()
        scrapeDescr=[
            {'key':'acronym', 'tag':'span','attribute':'class', 'value':'CEURVOLACRONYM'},
            {'key':'title',   'tag':'span','attribute':'class', 'value':'CEURFULLTITLE'},
            {'key':'loctime', 'tag':'span','attribute':'class', 'value':'CEURLOCTIME'}
        ]
        scrapedDict=scrape.parseWithScrapeDescription(url,scrapeDescr)
        if self.debug:
            print(scrapedDict)
        self.assertEqual('DL4KG2020',scrapedDict["acronym"])
        self.assertEqual('Heraklion, Greece, June 02, 2020',scrapedDict["loctime"])
        self.assertEqual('Proceedings of the Workshop on Deep Learning for Knowledge Graphs (DL4KG2020)',scrapedDict["title"])
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()