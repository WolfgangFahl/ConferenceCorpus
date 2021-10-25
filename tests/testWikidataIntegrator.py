'''
Created on 2021-10-24

@author: wf
'''
import unittest
from wikidataintegrator import wdi_core
import json

class TestWikidataIntegrator(unittest.TestCase):
    '''
    test access to Wikidata
    '''
    def prettyJson(self,jsonStr):
        parsed = json.loads(jsonStr)
        print(json.dumps(parsed, indent=2, sort_keys=True))

    def testQ5(self):
        '''
        test Q5 access
        '''
        q5 = wdi_core.WDItemEngine(wd_item_id='Q5')

        # to check successful installation and retrieval of the data, you can print the json representation of the item
        q5dict=q5.get_wd_json_representation()
        
        self.prettyJson(json.dumps(q5dict))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()