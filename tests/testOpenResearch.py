'''
Created on 27.07.2021

@author: wf
'''
import os
from functools import partial
from corpus.datasources.openresearch import OREventSeries, OREventSeriesManager, OREventManager, OREvent, OR
from tests.testSMW import TestSMW
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup, CorpusLookupConfigure


class TestOpenResearch(DataSourceTest):
    '''
    test the access to OpenResearch
    
    '''

    def setUp(self, debug=False,profile=True, **kwargs):
        super().setUp(debug, profile, **kwargs)
        # by convention the lookupId "or" is for the OpenResearch via API / WikiUser access
        # the lookupId "orclone" is for for the access via API on the OpenResearch clone
        lookupIds=[]
        self.testWikiId = "orclone"
        TestSMW.getWikiUser(self.testWikiId)
        self.testLimit=5
        OR.limitFiles=self.testLimit
        for wikiId in "or","orclone":
            wikiTextPath=CorpusLookupConfigure.getWikiTextPath(wikiId)
            if not os.path.exists(wikiTextPath):
                msg=f"wikibackup for {wikiId} missing you might want to run scripts/getbackup"
                raise Exception(msg)
            lookupIds.append(wikiId)
            lookupIds.append(f"{wikiId}-backup")
        self.lookup = CorpusLookup(lookupIds=lookupIds,configure=self.configureCorpusLookup)

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
        self.lookup.load()
        expectedSeries = OR.limitFiles if OR.limitFiles is not None else 1000
        expectedEvents = OR.limitFiles if OR.limitFiles is not None else 8000
        orDataSource=self.lookup.getDataSource("or-backup")
        self.checkDataSource(orDataSource,expectedSeries,expectedEvents)
        orDataSource=self.lookup.getDataSource("orclone-backup")
        self.checkDataSource(orDataSource,expectedSeries,expectedEvents)


    def testORDataSourceFromWikiUser(self):
        '''
        tests initializing the OREventCorpus from wiki
        '''
        self.lookup.load()
        expectedSeries = OR.limitFiles if OR.limitFiles is not None else 1000
        expectedEvents = OR.limitFiles if OR.limitFiles is not None else 8000
        orDataSource=self.lookup.getDataSource("or")
        self.checkDataSource(orDataSource, expectedSeries, expectedEvents)
        orDataSource=self.lookup.getDataSource("orclone")
        self.checkDataSource(orDataSource, expectedSeries, expectedEvents)

    def testAsCsv(self):
        '''
        test csv export of events
        '''
        return
        orDataSource =self.lookup.getDataSource("orclone-backup")
        eventManager=orDataSource.eventManager
        csvString=eventManager.asCsv(selectorCallback=partial(eventManager.getEventsInSeries, "3DUI"))
        print(csvString)

    def testEventSeriesGetLoDfromWikiFileManager(self):
        '''
        tests getLoDfromWikiFileManager from OREventSeries
        '''
        manager = OREventSeriesManager()
        wikiFileManager = TestSMW.getWikiFileManager(self.testWikiId)
        lod = manager.getLoDfromWikiFileManager(wikiFileManager=wikiFileManager, limit=self.testLimit)
        self.checkEntityLoD(lod, OREventSeries, self.testLimit)

    def testEventGetLoDfromWikiFileManager(self):
        '''
        tests getLoDfromWikiFileManager from OREvent
        '''
        manager = OREventManager()
        wikiFileManager = TestSMW.getWikiFileManager(self.testWikiId)
        lod = manager.getLoDfromWikiFileManager(wikiFileManager=wikiFileManager, limit=self.testLimit)
        self.checkEntityLoD(lod, OREvent, self.testLimit)

    def testEventSeriesGetLoDfromWikiUser(self):
        '''
        tests getLoDfromWikiUser from OREventSeries
        '''
        manager = OREventSeriesManager()
        wikiUser = TestSMW.getWikiUser(self.testWikiId)
        lod = manager.getLoDfromWikiUser(wikiuser=wikiUser, limit=self.testLimit)
        self.checkEntityLoD(lod, OREventSeries, self.testLimit)

    def testEventGetLoDfromWikiUser(self):
        '''
        tests getLoDfromWikiUser from OREvent
        '''
        manager = OREventManager()
        wikiUser = TestSMW.getWikiUser(self.testWikiId)
        lod = manager.getLoDfromWikiUser(wikiuser=wikiUser, limit=self.testLimit)
        self.checkEntityLoD(lod, OREvent, self.testLimit)

    def checkEntityLoD(self, lod:dict, entity:type, expectedRecords:int=None):
        """
        checks if the given lod contains the mandatory fields of the given entity
        Args:
            lod: list of entity records
            entity: entity class containing the samples with the mandatory fields
        """
        if self.debug:
            print(lod)
        mandatoryFields = set(entity().getSamples()[0].keys())
        if expectedRecords is not None:
            self.assertEqual(len(lod), expectedRecords, "LoD does not contain expected number of records")
        for record in lod:
            fields = set(record.keys())
            self.assertTrue(mandatoryFields.issubset(fields), f"Mandatory fields {mandatoryFields - fields} are missing")
            self.assertIsNotNone(record["pageTitle"])




if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    DataSourceTest.main()