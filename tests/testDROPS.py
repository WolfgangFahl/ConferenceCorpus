'''
Created on 2022-03-03

@author: wf
'''
import unittest
from tests.datasourcetoolbox import DataSourceTest
from corpus.datasources.drops import DROPS


class TestDROPS(DataSourceTest):
    '''
    Dagstuhl Research Online Publication Server Volumes
    https://github.com/WolfgangFahl/ConferenceCorpus/issues/38
    '''

    def setUp(self):
        super().setUp()
        self.maxCollectionId=812 
        
    def testCaching(self):
        '''
        test getting the DROPS metadata
        
        '''
        drops=DROPS(self.maxCollectionId)
        for cid in range(1,drops.maxCollectionId+1):
            drops.cache(cid)
       
    def testParsing(self):   
        #debug=self.debug
        debug=True
        #XmlEntity.debug=debug
        drops=DROPS(self.maxCollectionId)
        volumes={}
        for cid in range(1,drops.maxCollectionId+1):  
            for volume in drops.parse(cid):
                volumes[volume.shortTitle]=volume
            pass
        if debug:
            print(f"found {len(volumes)} volumes")
        expected=321
        self.assertTrue(len(volumes)>=expected)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()