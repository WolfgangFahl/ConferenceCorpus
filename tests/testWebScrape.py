'''
Created on 2021-07-31

@author: wf
'''
import unittest
from corpus.datasources.webscrape import WebScrape
from corpus.datasources.wikicfpscrape import CrawlType
from tests.datasourcetoolbox import DataSourceTest


class TestWebScrape(DataSourceTest):
    '''
    test getting rdfA based triples from Webpages
    '''

    def testCrawlType(self):
        '''
        test CrawlType isValid
        '''
        self.assertTrue(CrawlType.isValid("Event"))
        self.assertFalse(CrawlType.isValid("Homepage"))

    def testWebScrape(self):
        '''
        test getting rdfA encoded info from a webpage
        '''
        debug=self.debug
        url="http://ceur-ws.org/Vol-2635/"
        scrape=WebScrape(timeout=20 if self.inCI() else 3)
        scrapeDescr=[
            {'key':'acronym', 'tag':'span','attribute':'class', 'value':'CEURVOLACRONYM'},
            {'key':'title',   'tag':'span','attribute':'class', 'value':'CEURFULLTITLE'},
            {'key':'loctime', 'tag':'span','attribute':'class', 'value':'CEURLOCTIME'}
        ]
        scrapedDict=scrape.parseWithScrapeDescription(url,scrapeDescr)
        if scrape.err:
            print(scrape.err)
            print("We might not be able to do anything about it")
            return
        if debug:
            print(scrapedDict)
        self.assertEqual('DL4KG2020',scrapedDict["acronym"])
        self.assertEqual('Heraklion, Greece, June 02, 2020',scrapedDict["loctime"])
        self.assertEqual('Proceedings of the Workshop on Deep Learning for Knowledge Graphs (DL4KG2020)',scrapedDict["title"])
        pass

    def test_findLinkByPrefixLabel(self):
        """
        tests findLinkByPrefixLabel
        """
        test_params = [
            ("http://www.wikicfp.com/cfp/servlet/event.showcfp?eventid=300", "http://wwwling.arts.kuleuven.be/nrg4"),
            ("http://www.wikicfp.com/cfp/servlet/event.showcfp?eventid=3", None)
        ]
        for (url, expected_homepage) in test_params:
            with self.subTest(url):
                scrape = WebScrape(debug=self.debug)
                triples = scrape.parseRDFa(url)
                extracted_homepage = scrape.findLinkByPrefixLabel("\w*Link:\w*")
                self.assertEqual(expected_homepage, extracted_homepage)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()