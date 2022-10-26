'''
Created on 2021-10-24

@author: wf
'''
from wikibaseintegrator import wbi_helpers

from tests.datasourcetoolbox import DataSourceTest
import json


class TestWikiBaseIntegrator(DataSourceTest):
    '''
    test access to Wikidata
    '''
    def prettyJson(self,jsonStr):
        parsed = json.loads(jsonStr)
        if self.debug:
            print(json.dumps(parsed, indent=2, sort_keys=True))

    def testQ5(self):
        '''
        test Q5 access
        '''
        query = {
    'action': 'query',
    'prop': 'revisions',
    'titles': 'Q5',
    'rvlimit': 10
}
        result=wbi_helpers.mediawiki_api_call_helper(query, allow_anonymous=True)
        self.prettyJson(json.dumps(result))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    DataSourceTest.main()