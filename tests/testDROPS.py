'''
Created on 2022-03-03

@author: wf
'''
import unittest
from tests.datasourcetoolbox import DataSourceTest
from corpus.datasources.drops import DROPS
from corpus.utils.progress import Progress


class TestDROPS(DataSourceTest):
    '''
    Dagstuhl Research Online Publication Server Volumes
    https://github.com/WolfgangFahl/ConferenceCorpus/issues/38
    '''

    def setUp(self, debug:bool=False, **kwargs):
        super().setUp(debug=debug, **kwargs)
        self.maxCollectionId=812 if not self.inCI() else 10
        
    def testCaching(self):
        '''
        test getting the DROPS metadata
        
        '''
        drops=DROPS(self.maxCollectionId)
        progress=Progress(progressSteps=1,expectedTotal=drops.maxCollectionId,showDots=True,msg="caching DROPS XML files",showMemory=True)
        for cid in range(1,drops.maxCollectionId+1):
            drops.cache(cid)
            progress.next()
        progress.done()
       
    def testParsing(self):   
        debug=self.debug
        debug=True
        #XmlEntity.debug=debug
        drops=DROPS(self.maxCollectionId)
        volumes={}
        progress=Progress(progressSteps=1,expectedTotal=drops.maxCollectionId,showDots=True,msg="parsing DROPS XML files",showMemory=True)
        for cid in range(1,drops.maxCollectionId+1):  
            for volume in drops.parse(cid):
                volumes[volume.shortTitle]=volume
                progress.next()
            pass
        progress.done()
        if debug:
            print(f"found {len(volumes)} volumes")
        expected=321 if not self.inCI() else 10
        self.assertGreaterEqual(len(volumes),expected)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()