'''
Created on 06.08.2021

@author: wf
'''
import unittest
from quality.painscale import PainScale
from urllib.request import urlopen


class TestPainScale(unittest.TestCase):
    '''
    test the PainScale see
    '''

    def setUp(self):
        self.debug=False
        pass


    def tearDown(self):
        pass


    def testPainImages(self):
        '''
        test Pain Images
        '''
        size=48
        for pain in range(0,11):
            url=PainScale.lookupPainImage(pain, size,asImageTag=False)
            imgTag=PainScale.lookupPainImage(pain, size,asImageTag=True)
            self.assertTrue(f"{size}px" in imgTag)
            resource = urlopen(url)
            content =  resource.read()
            imageSize=len(content)
            if self.debug:
                print(f"pain {pain} image has size {imageSize}")
            self.assertTrue(len(content)>3000)
            pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()