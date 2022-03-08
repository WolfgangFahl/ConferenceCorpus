'''
Created on 27.07.2021

@author: wf
'''
from functools import partial
from tests.testSMW import TestSMW
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup

class TestOpenResearch(DataSourceTest):
    '''
    test the access to OpenResearch
    
    '''

    def setUp(self):
        DataSourceTest.setUp(self)
        # by convention the lookupId "or" is for the OpenResearch via API / WikiUser access
        # the lookupId "orclone" is for for the access via API on the OpenResearch clone
        self.lookup = CorpusLookup(lookupIds=["or", "or-backup", "orclone", "orclone-backup"],configure=self.configureCorpusLookup)
        self.lookup.load(forceUpdate=True)   # forceUpdate=True to test the filling of the cache

    def configureCorpusLookup(self,lookup:CorpusLookup):
        '''
        callback to configure the corpus lookup
        '''        
        for lookupId in ["or","orclone"]:
            orDataSource=lookup.getDataSource(lookupId)
            if orDataSource:
                wikiUser=TestSMW.getSMW_WikiUser(lookupId)
                orDataSource.eventManager.wikiUser=wikiUser
                orDataSource.eventSeriesManager.wikiUser=wikiUser
            orDataSource=lookup.getDataSource(f'{lookupId}-backup')
            if orDataSource:
                wikiFileManager = TestSMW.getWikiFileManager(wikiId=lookupId)
                orDataSource.eventManager.wikiFileManager = wikiFileManager
                orDataSource.eventSeriesManager.wikiFileManager = wikiFileManager

    def testORDataSourceFromWikiFileManager(self):
        '''
        tests the getting conferences form wiki markup files
        '''
        orDataSource=self.lookup.getDataSource("or-backup")
        self.checkDataSource(orDataSource,1000,8000)
        orDataSource=self.lookup.getDataSource("orclone-backup")
        self.checkDataSource(orDataSource,1000,8000)


    def testORDataSourceFromWikiUser(self):
        '''
        tests initializing the OREventCorpus from wiki
        '''
        orDataSource=self.lookup.getDataSource("or")
        self.checkDataSource(orDataSource,1000,8000)
        orDataSource=self.lookup.getDataSource("orclone")
        self.checkDataSource(orDataSource,1000,8000)

    def testAsCsv(self):
        '''
        test csv export of events
        '''
        return
        orDataSource =self.lookup.getDataSource("orclone-backup")
        eventManager=orDataSource.eventManager
        csvString=eventManager.asCsv(selectorCallback=partial(eventManager.getEventsInSeries, "3DUI"))
        print(csvString)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    DataSourceTest.main()