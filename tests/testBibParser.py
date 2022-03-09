'''
Created on 2022-01-12

@author: wf
'''
import unittest
from bibtex.bibparser import BibParser
from tests.datasourcetoolbox import DataSourceTest

class TestBibParser(DataSourceTest):
    '''
    test a bib parser
    '''

    def setUp(self):
        DataSourceTest.setUp(self)
        pass

    def testBibParser(self):
        '''
        test Bibtex parser
        '''
        bp=BibParser()
        url="https://jens-lehmann.org/files/cv.bib"
        bibData=bp.parseUrl(url)
        debug=self.debug
        #debug=True
        if debug:
            print(bibData)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    DataSourceTest.main()