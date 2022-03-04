'''
Created on 04.03.2022

@author: wf
'''
from tests.datasourcetoolbox import DataSourceTest
import getpass
from corpus.datasources.tibkat import FTXParser
from corpus.xml.xmlparser import XmlEntity

class TestFTXParser(DataSourceTest):
    '''
    test FTX parsing
    '''
    
    def setUp(self,debug=False,profile=True):
        super().setUp(debug=debug, profile=profile)
        user=getpass.getuser()
        self.ftxroot=None
        self.ftxParser=None
        if user=="wf":
            self.ftxroot="/Volumes/seel/tibkat-ftx/tib-intern-ftx_0/tib-2021-12-20"
        if self.ftxroot is not None:
            self.ftxParser=FTXParser(self.ftxroot)
        self.sampleFtx="tib-intern-ftx_2021-12-20_T201424_5766.xml"
            
    def testFtxXmlFiles(self):
        '''
        check listing the FTX xml files
        '''
        debug=self.debug
        #debug=True
        if self.ftxParser is not None:
            self.xmlFiles=self.ftxParser.ftxXmlFiles()
            if debug:
                print(f"found {len(self.xmlFiles)} FTX files")
            self.assertTrue(len(self.xmlFiles)>7600)
            
    def testDocumentParsing(self):
        '''
        test parsing documents out of the FTX xml file
        '''
        debug=self.debug
        debug=True
        show=True
        XmlEntity.debug=debug
        if self.ftxParser is not None:
            xmlPath=f"{self.ftxroot}/{self.sampleFtx}"
            documents={}
            for document in self.ftxParser.parse(xmlPath):
                if debug:
                    print(document)
                documents[document.ppn]=document
            if debug:
                print (f"found {len(documents)} documents")    
            self.assertEqual(100,len(documents))
            ppns=[
                "579171965", # ISWC 2008
                #"578841517" # SoftVis  2008
            ]
            for ppn in ppns:
                self.assertTrue(ppn in documents)
                document=documents[ppn]
                if debug and hasattr(document,"rawxml"):
                    print(document.rawxml)
                if show:
                    print(document)
            