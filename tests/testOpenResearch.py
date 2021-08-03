'''
Created on 27.07.2021

@author: wf
'''
import unittest
from tests.testSMW import TestSMW
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup

class TestOpenResearch(DataSourceTest):
    '''
    test the access to OpenResearch
    
    '''

    def setUp(self):
        DataSourceTest.setUp(self)
        pass

    def configureCorpusLookup(self,lookup:CorpusLookup):
        '''
        callback to configure the corpus lookup
        '''        
        for lookupId in ["or","orclone"]:
            orDataSource=lookup.getDataSource(lookupId)
            wikiFileManager=TestSMW.getWikiFileManager(wikiId=lookupId)
            orDataSource.eventManager.wikiFileManager=wikiFileManager
            orDataSource.eventSeriesManager.wikiFileManager=wikiFileManager
            orDataSource=lookup.getDataSource(f'{lookupId}-backup')
            wikiUser=TestSMW.getSMW_WikiUser(lookupId)
            orDataSource.eventManager.wikiUser=wikiUser
            orDataSource.eventSeriesManager.wikiUser=wikiUser

    def testORDataSourceFromWikiFileManager(self):
        '''
        tests the getting conferences form wiki markup files
        '''
        lookup=CorpusLookup(lookupIds=["or","or-backup","orclone","orclone-backup"],configure=self.configureCorpusLookup)
        lookup.load(forceUpdate=False)
        orDataSource=lookup.getDataSource("or-backup")
        self.checkDataSource(orDataSource,1000,8000)
        orDataSource=lookup.getDataSource("orclone-backup")
        self.checkDataSource(orDataSource,1000,8000)


    def testORDataSourceFromWikiUser(self):
        '''
        tests initializing the OREventCorpus from wiki
        '''
        # by convention the lookupId "or" is for the OpenResearch via API / WikiUser access
        # the lookupId "orclone" is for for the access via API on the OpenResearch clone
        lookup=CorpusLookup(lookupIds=["or","or-backup","orclone","orclone-backup"],configure=self.configureCorpusLookup)
        lookup.load(forceUpdate=False)
        orDataSource=lookup.getDataSource("or")
        self.checkDataSource(orDataSource,1000,8000)
        orDataSource=lookup.getDataSource("orclone")
        self.checkDataSource(orDataSource,1000,8000)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()