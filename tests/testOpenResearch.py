'''
Created on 27.07.2021

@author: wf
'''
import os
from functools import partial
from pathlib import Path
from corpus.datasources.openresearch import OREventSeries, OREventSeriesManager, OREventManager, OREvent, OR, OrSMW
from tests.basetest import BaseTest
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
        self.testLimit=100
        OR.limitFiles=self.testLimit
        for wikiId in "or","orclone":
            wikiTextPath=CorpusLookupConfigure.getWikiTextPath(wikiId)
            if not os.path.exists(wikiTextPath):
                msg=f"wikibackup for {wikiId} missing you might want to run scripts/getbackup"
                raise Exception(msg)
            lookupIds.append(wikiId)
            lookupIds.append(f"{wikiId}-backup")
        self.lookup = CorpusLookup(lookupIds=lookupIds)

    def testORDataSourceFromWikiFileManager(self):
        '''
        tests the getting conferences form wiki markup files
        '''
        expectedSeries = OR.limitFiles if OR.limitFiles is not None else 1000
        expectedEvents = OR.limitFiles if OR.limitFiles is not None else 8000
        for wikiId in ['or', 'orclone']:
            datasource = self.lookup.getDataSource(f"{wikiId}-backup")
            self.checkDataSource(datasource, expectedSeries, expectedEvents)

    def testORDataSourceFromWikiUser(self):
        '''
        tests initializing the OREventCorpus from wiki
        '''
        self.lookup.load()
        expectedSeries = OR.limitFiles if OR.limitFiles is not None else 1000
        expectedEvents = OR.limitFiles if OR.limitFiles is not None else 8000
        for wikiId in ['or', 'orclone']:
            datasource = self.lookup.getDataSource(f"{wikiId}")
            self.checkDataSource(datasource, expectedSeries, expectedEvents)

    def testAsCsv(self):
        '''
        test csv export of events
        '''
        self.lookup.load()
        orDataSource =self.lookup.getDataSource("orclone-backup")
        eventManager=orDataSource.eventManager
        csvString=eventManager.asCsv(selectorCallback=partial(eventManager.getEventsInSeries, "3DUI"))
        if self.debug:
            print(csvString)
        self.assertIn("3DUI 2016", csvString)


class TestOREventManager(DataSourceTest):
    """
    Tests OREventManager
    """

    def setUp(self,debug=False,profile=True,timeLimitPerTest=10.0):
        super().setUp(debug, profile, timeLimitPerTest)
        self.wikiId = "orclone"
        TestSMW.getWikiUser(self.wikiId)
        self.loadingMethods = {
            "wikiMarkup": OREventManager.getLodFromWikiMarkup.__name__,
            "backup": OREventManager.getLoDfromWikiFileManager.__name__,
            "api": OREventManager.getLoDfromWikiUser.__name__
        }
        self.limit = 5

    def test_configure(self):
        """
        tests configuring OREventManager with different loading methods to retrieve the records from the source
        """
        for via, expectedFn in self.loadingMethods.items():
            manager = OREventManager(wikiId=self.wikiId, via=via)
            manager.configure()
            self.assertEqual(getattr(manager, expectedFn), manager.getListOfDicts)

    def test_getLodFrom(self):
        """
        tests the different loading methods
        Note: the functionality is tested in depth in TestOrSMW here only te enhancing of the records is tested
        """
        for via, expectedFn in self.loadingMethods.items():
            manager = OREventManager(wikiId=self.wikiId, via=via)
            lod = getattr(manager, expectedFn)(limit=self.limit)
            self.assertEqual(self.limit, len(lod))
            for d in lod:
                self.assertEqual(f"{self.wikiId}-{via}", d.get('source'))

    def test_fromWikiUser(self):
        """
        tests fromWikiUser
        """
        manager = OREventManager(wikiId=self.wikiId, via="api")
        self.assertEqual([], manager.getList())
        manager.fromWikiUser(limit=self.limit)
        self.assertEqual(self.limit, len(manager.getList()))
        self.assertIsInstance(manager.getList()[0], OREvent)

    def test_fromWikiFileManager(self):
        """
        tests fromWikiFileManager
        """
        manager = OREventManager(wikiId=self.wikiId, via="backup")
        self.assertEqual([], manager.getList())
        manager.fromWikiFileManager(limit=self.limit)
        self.assertEqual(self.limit, len(manager.getList()))
        self.assertIsInstance(manager.getList()[0], OREvent)

    def test_getPropertyLookup(self):
        """
        tests getPropertyLookup
        """
        lookup = OREventManager.getPropertyLookup()
        self.assertIn('GND-ID', lookup)
        self.assertEqual(3, len(lookup.get('Acronym')))
        self.assertEqual(len(OREvent.propertyLookupList), len(lookup))


class TestOREventSeriesManager(DataSourceTest):
    """
    Tests OREventSeriesManager
    """

    def setUp(self,debug=False,profile=True,timeLimitPerTest=10.0):
        super().setUp(debug, profile, timeLimitPerTest)
        self.wikiId = "orclone"
        TestSMW.getWikiUser(self.wikiId)
        self.loadingMethods = {
            "wikiMarkup": OREventSeriesManager.getLodFromWikiMarkup.__name__,
            "backup": OREventSeriesManager.getLoDfromWikiFileManager.__name__,
            "api": OREventSeriesManager.getLoDfromWikiUser.__name__
        }
        self.limit = 5

    def test_configure(self):
        """
        tests configuring OREventManager with different loading methods to retrieve the records from the source
        """
        for via, expectedFn in self.loadingMethods.items():
            manager = OREventSeriesManager(wikiId=self.wikiId, via=via)
            manager.configure()
            self.assertEqual(getattr(manager, expectedFn), manager.getListOfDicts)

    def test_getLodFrom(self):
        """
        tests the different loading methods
        Note: the functionality is tested in depth in TestOrSMW here only te enhancing of the records is tested
        """
        for via, expectedFn in self.loadingMethods.items():
            manager = OREventSeriesManager(wikiId=self.wikiId, via=via)
            lod = getattr(manager, expectedFn)(limit=self.limit)
            self.assertEqual(self.limit, len(lod))
            for d in lod:
                self.assertEqual(f"{self.wikiId}-{via}", d.get('source'))

    def test_fromWikiUser(self):
        """
        tests fromWikiUser
        """
        manager = OREventSeriesManager(wikiId=self.wikiId, via="api")
        self.assertEqual([], manager.getList())
        manager.fromWikiUser(limit=self.limit)
        self.assertEqual(self.limit, len(manager.getList()))
        self.assertIsInstance(manager.getList()[0], OREventSeries)

    def test_fromWikiFileManager(self):
        """
        tests fromWikiFileManager
        """
        manager = OREventSeriesManager(wikiId=self.wikiId, via="backup")
        self.assertEqual([], manager.getList())
        manager.fromWikiFileManager(limit=self.limit)
        self.assertEqual(self.limit, len(manager.getList()))
        self.assertIsInstance(manager.getList()[0], OREventSeries)

    def test_getPropertyLookup(self):
        """
        tests getPropertyLookup
        """
        lookup = OREventSeriesManager.getPropertyLookup()
        self.assertIn('GND-ID', lookup)
        self.assertEqual(3, len(lookup.get('Title')))
        self.assertEqual(len(OREventSeries.propertyLookupList), len(lookup))


class TestOrSMW(BaseTest):
    """
    tests OrSWM
    """

    def setUp(self, debug:bool=False, profile:bool=True):
        super().setUp(debug, profile)
        self.wikiId = "orclone"
        TestSMW.getWikiUser(self.wikiId)

    def test_getAskQuery(self):
        """
        tests getAskQuery
        """
        for entityType in [OREvent, OREventSeries]:
            askQuery = OrSMW.getAskQuery(entityType)
            if self.debug:
                print(askQuery)
            self.assertIn(entityType.entityName, askQuery)
            for prop, name in entityType.getPropertyLookup().items():
                self.assertIn(f"?{prop}={name}", askQuery)

    def test_getAskQueryPageTitles(self):
        """
        tests getAskQueryPageTitles
        """
        for entityType in [OREvent, OREventSeries]:
            askQuery = OrSMW.getAskQueryPageTitles(entityType)
            self.assertIn(f"[[IsA::{entityType.entityName}]]", askQuery)
            self.assertIn("pageTitle", askQuery)

    def test_getLodFromWikiMarkup(self):
        """
        tests getLodFromWikiMarkup
        """
        limit = 5
        for entityType in [OREvent, OREventSeries]:
            lod = OrSMW.getLodFromWikiMarkup(self.wikiId, entityType=entityType, limit=limit, showProgress=False)
            self.assertEqual(limit, len(lod))
            expectedProps = [r.get('name') for r in entityType.propertyLookupList]
            mandatoryProperties = ['pageTitle', 'wikiMarkup']
            expectedProps.extend(mandatoryProperties)
            for d in lod:
                for mp in mandatoryProperties:
                    self.assertIn(mp, d)
                for prop in d:
                    self.assertIn(prop, expectedProps)
                if self.debug or True:
                    print(f"{d.get('pageTitle')}: {d}")

    def test_getLodFromWikiApi(self):
        """
        tests getLodFromWikiApi
        """
        limit = 5
        for entityType in [OREvent, OREventSeries]:
            lod = OrSMW.getLodFromWikiApi(self.wikiId, entityType=entityType, limit=limit)
            self.assertEqual(limit, len(lod))
            expectedProps = [r.get('name') for r in entityType.propertyLookupList]
            expectedProps.extend(["pageTitle", "modificationDate", "creationDate", "lastEditor"])
            for d in lod:
                self.assertIn('pageTitle', d)
                for prop in d:
                    self.assertIn(prop, expectedProps)

    def test_getLodFromWikiFiles(self):
        """
        tests getLodFromWikiFiles
        """
        defaultQikiTextPath = f"{Path.home()}/.or/wikibackup/{self.wikiId}"
        numberBackupFiles = len([name for name in os.listdir(defaultQikiTextPath) if os.path.isfile(os.path.join(defaultQikiTextPath, name))])
        if numberBackupFiles >= 500:
            # backup is present test extraction
            limit = 5
            for entityType in [OREvent, OREventSeries]:
                lod = OrSMW.getLodFromWikiFiles(self.wikiId, entityType=entityType, limit=limit)
                self.assertEqual(limit, len(lod))
                expectedProps = [r.get('name') for r in entityType.propertyLookupList]
                mandatoryProperties = ['pageTitle', 'wikiMarkup']
                expectedProps.extend(mandatoryProperties)
                for d in lod:
                    for mp in mandatoryProperties:
                        self.assertIn(mp, d)
                    for prop in d:
                        self.assertIn(prop, expectedProps)

    def test_getLodFromWikiMarkup_queryAllEvents(self):
        """
        tests querying all events with getLodFromWikiApi to check if the query division works
        """
        return   # test takes ~20 min. only needs to be tested if query division seems not to work properly
        lod = OrSMW.getLodFromWikiMarkup(self.wikiId, entityType=OREvent)
        if self.debug:
            total = len(lod)
            for i, d in enumerate(lod):
                print(f"({i}/{total}) {d}")
        self.assertGreaterEqual(len(lod), 9850)

    def test_normalizeProperties(self):
        """
        tests normalizeProperties
        """
        propMap = OREvent.getTemplateParamLookup()
        template_dict = {k: "test value" for k in propMap.keys()}
        normalized_dict = {v: "test value" for v in propMap.values()}
        self.assertDictEqual(normalized_dict, OrSMW.normalizeProperties(template_dict, OREvent))
        self.assertDictEqual(template_dict, OrSMW.normalizeProperties(normalized_dict, OREvent, reverse=True))
        # test exclusion
        unkown_prop = {"unkown_key":"This property should be excluded"}
        extended_dict = {**unkown_prop, **template_dict}
        self.assertDictEqual(normalized_dict, OrSMW.normalizeProperties(extended_dict, OREvent))
        self.assertDictEqual({**unkown_prop, **normalized_dict}, OrSMW.normalizeProperties(extended_dict, OREvent, force=True))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    DataSourceTest.main()