'''
Created on 06.08.2021

@author: wf
'''
from corpus.quality.painscale import PainScale
from urllib.request import urlopen
from tests.datasourcetoolbox import DataSourceTest

class TestPainScale(DataSourceTest):
    '''
    test the PainScale see
    '''

    def setUp(self, debug:bool=False, profile:bool=True, **kwargs):
        super().setUp(debug=debug, profile=profile, **kwargs)

    def testPainImages(self):
        '''
        test Pain Images
        '''
        size=48
        for pain in range(0,11):
            url=PainScale.lookupPainImage(pain, size,asImageTag=False)
            imgTag=PainScale.lookupPainImage(pain, size,asImageTag=True)
            self.assertTrue(f"{size}px" in imgTag)
            content=None
            try:
                resource = urlopen(url)
                content =  resource.read()
            except Exception as ex:
                if self.debug:
                    f"{url} - failed with {str(ex)}"
            self.assertIsNotNone(content,f"{url}")
            imageSize=len(content)
            if self.debug:
                print(f"pain {pain} image has size {imageSize}")
            self.assertTrue(len(content)>3000)
            pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    DataSourceTest.main()