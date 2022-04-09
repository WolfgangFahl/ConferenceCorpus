'''
Created on 2022-04-09

@author: wf
'''
from tests.basetest import BaseTest
from corpus.event import EventStorage

class TestEventStorage(BaseTest):
    '''
    test the event storage functionality
    '''

    def testGetPlantUmlDiagram(self):
        '''
        test creating a plantuml diagram of the tables involved in the lookup
        '''
        debug=self.debug
        debug=True
        storageTableList=EventStorage.getTableList()
        if debug:
            print(f"found {len(storageTableList)} storage Tables for the ConferenceCorpus")
        #self.assertEqual(22,len(storageTableList))
        for baseEntity in ["Event","EventSeries"]:
            plantUml=EventStorage.asPlantUml(baseEntity,exclude=EventStorage.viewTableExcludes)
            if debug:
                print(plantUml)
            self.assertTrue(f"{baseEntity} <|-- {baseEntity.lower()}_dblp" in plantUml)
            self.assertTrue(f"class {baseEntity} " in plantUml)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()