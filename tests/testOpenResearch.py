'''
Created on 27.07.2021

@author: wf
'''
from functools import partial
from tests.testSMW import TestSMW
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup,CorpusLookupConfigure
import os
class TestOpenResearch(DataSourceTest):
    '''
    test the access to OpenResearch
    
    '''

    def setUp(self):
        DataSourceTest.setUp(self)
        # by convention the lookupId "or" is for the OpenResearch via API / WikiUser access
        # the lookupId "orclone" is for for the access via API on the OpenResearch clone
        lookupIds=[]
        for wikiId in "or","orclone":
            wikiTextPath=CorpusLookupConfigure.getWikiTextPath(wikiId)
            if not os.path.exists(wikiTextPath):
                msg="wikibackup for {wikiId} missing you might want to run scripts/getbackup"
                raise Exception(msg)
            lookupIds.append(wikiId)
            lookupIds.append(f"{wikiId}-backup")
        self.lookup = CorpusLookup(lookupIds=lookupIds,configure=self.configureCorpusLookup)
        self.lookup.load(forceUpdate=True)   # forceUpdate=True to test the filling of the cache

    def setWikiUserAndOptions(self,manager,wikiUser,debug,profile=True):
        manager.wikiUser=wikiUser
        manager.debug=debug
        manager.config.withShowProgress=profile
        manager.profile=profile
    
    def setWikiFileManagerAndOptions(self,manager,fileManager,debug,profile=True):
        manager.wikiFileManager=fileManager
        manager.debug=debug
        manager.config.withShowProgress=profile
        manager.profile=profile
        
    def configureCorpusLookup(self,lookup:CorpusLookup):
        '''
        callback to configure the corpus lookup
        '''
        for lookupId in ["or","orclone"]:
            orDataSource=lookup.getDataSource(lookupId)
            if orDataSource:
                orDataSource.profile=True
                orDataSource.debug=self.debug
                wikiUser=TestSMW.getSMW_WikiUser(lookupId)
                self.setWikiUserAndOptions(orDataSource.eventManager, wikiUser, self.debug)
                self.setWikiUserAndOptions(orDataSource.eventSeriesManager, wikiUser, self.debug)
            orDataSource=lookup.getDataSource(f'{lookupId}-backup')
            if orDataSource:
                orDataSource.profile=True
                orDataSource.debug=self.debug
                wikiFileManager = TestSMW.getWikiFileManager(wikiId=lookupId)
                self.setWikiFileManagerAndOptions(orDataSource.eventManager, wikiFileManager, self.debug)
                self.setWikiFileManagerAndOptions(orDataSource.eventSeriesManager,wikiFileManager, self.debug)

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