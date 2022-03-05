'''
Created on 2021-08-02

@author: wf
'''
import unittest
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup
from corpus.datasources.crossref import Crossref,CrossrefEvent, CrossrefEventManager
import json

class TestCrossRef(DataSourceTest):
    '''
    test getting events from CrossRef https://www.crossref.org/
    as a data source
    '''

    def setUp(self):
        DataSourceTest.setUp(self)
        pass


    def testCrossRef(self):
        '''
        test CrossRef as an event data source
        '''
        lookup=CorpusLookup(lookupIds=["crossref"])
        lookup.load(forceUpdate=False)
        crossRefDataSource=lookup.getDataSource("crossref")
        _eventSeriesList,_eventList=self.checkDataSource(crossRefDataSource,0,40000,eventSample="SIGMIS CPR '06")
        pass
    
    def testFixUmlauts(self):
        '''
        workaround Umlaut issue see https://stackoverflow.com/questions/63486767/how-can-i-get-the-fuseki-api-via-sparqlwrapper-to-properly-report-a-detailed-err
        '''
        eventInfo={'location':'M\\\"unster, Germany'}
        Crossref.fixEncodings(eventInfo,debug=self.debug)
        self.assertEqual(eventInfo['location'],"Münster, Germany")
        
        
    def prettyJson(self,d):
        '''
        prettry print the given jsonStr
        '''
        jsonStr=json.dumps(d,indent=2,sort_keys=True)
        print(jsonStr)
        
    def testCrossref_DOI_Lookup(self):
        ''' test crossref API access 
        see https://github.com/WolfgangFahl/ProceedingsTitleParser/issues/28
        '''
        cr=Crossref()
        dois=['10.1637/0005-2086-63.1.117','10.1145/3001867']
        expected=[
            {'title':'Tenth International Symposium on Avian Influenza'},
            {'title':'Proceedings of the 7th International Workshop on Feature-Oriented Software Development'}
        ]
        debug=self.debug
        for index,doi in enumerate(dois):
            doimeta=cr.doiMetaData(doi)
            if debug:
                self.prettyJson (doimeta)
            self.assertTrue('title' in doimeta)
            title=doimeta['title'][0]
            if self.debug:
                print (title)
            self.assertEqual(expected[index]['title'],title)
        pass
    
    def testCrossRefEventFromDOI(self):
        '''
        test creating CrossRefEvents via API
        '''
        dois=['10.7551/978-0-262-33027-5']
        expectedList=[
            {
                'source': 'crossref',
                'acronym':'ECAL 2015',
                'title': 'European Conference on Artificial Life 2015'
            }
             
        ]
        debug=self.debug
        #debug=True
        for index,doi in enumerate(dois):
            event=CrossrefEvent.fromDOI(doi)
            if debug:
                print(f"#{index:2}:{doi:40}→{event}")
                print(event.metadata)
            expected=expectedList[index]
            for key in expected:
                self.assertEqual(expected[key],getattr(event,key))
    


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()