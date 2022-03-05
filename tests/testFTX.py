'''
Created on 04.03.2022

@author: wf
'''
from tests.datasourcetoolbox import DataSourceTest
import getpass
from corpus.datasources.tibkatftx import FTXParser
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
        self.sampleBase="tib-intern-ftx_2021-12-20_"
        self.samples=["T184133_3056","T201424_5766","T184335_3113","T182353_2562","T191138_3961"]
        self.sampleFtxs=[]
        for sample in self.samples:
            self.sampleFtxs.append(f"{self.sampleBase}{sample}.xml")
    
    def getAllFtxXmlFiles(self):
        if not hasattr(self, "xmlFiles"):
            self.xmlFiles=self.ftxParser.ftxXmlFiles()
            if self.debug:
                print(f"found {len(self.xmlFiles)} FTX files")
        return self.xmlFiles
        
    def testFtxXmlFiles(self):
        '''
        check listing the FTX xml files
        '''
        if self.ftxParser is not None:
            self.getAllFtxXmlFiles()
            self.assertTrue(len(self.xmlFiles)>7600)
            
    def testDocumentParsing(self):
        '''
        test parsing documents out of the FTX xml file
        '''
        debug=self.debug
        #debug=True
        show=True
        #show=False
        XmlEntity.debug=debug
        if self.ftxParser is not None:
            documents={}
            for sampleFtx in self.sampleFtxs:
                for document in self.ftxParser.parse(sampleFtx,local=True):
                    if debug:
                        print(document)
                    ppn=document.ppn
                    documents[ppn]=document
                if debug:
                    print (f"found {len(documents)} documents in {sampleFtx}")    
            self.assertEqual(100*len(self.sampleFtxs),len(documents))
            ppns=[
                "579171965", # ISWC 2008
                #"578841517" # SoftVis  2008
                #"1662974825" # SafeAI 2019
                "1677843861", # AAAI 2018
                "668314257", #
                "1745369562"
            ]
            for ppn in ppns:
                self.assertTrue(ppn in documents)
                document=documents[ppn]
                if debug and hasattr(document,"rawxml"):
                    print(document.rawxml)
                if show:
                    print(document)
                    
    def testParseAll(self):
        '''
        test parse all ftx files
        '''
        if self.ftxParser is not None:
            self.getAllFtxXmlFiles()
            count=0
            for xmlFile in self.xmlFiles:
                for document in self.ftxParser.parse(xmlFile,local=True):
                    count+=1
                    if count%1000==0:
                        print(".",end="")
                    if count%10000==0:
                        print(f"{count}",end="")
                    if count%80000==0:
                        print()