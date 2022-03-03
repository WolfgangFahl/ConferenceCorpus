'''
Created on 2022-03-03

@author: wf
'''
from corpus.datasources.download import Download
from os import path
import os
import urllib
from xml.etree.ElementTree import Element
from xml.etree import cElementTree as ElementTree
from xml.etree.ElementTree import ParseError
from typing import Iterator

class XmlEntity(object):
    '''
    an entity based on an XML object
    '''
    debug=False
    
    def __init__(self,element:Element,xmlPropertyMap:dict,namespaces:dict):
        ''' 
        constructor
        
        Args:
            element: the element to construct me from
        '''
        self._props=[]
        if XmlEntity.debug:
            xml=ElementTree.tostring(element)
            print(xml)
        for prop, xpath in xmlPropertyMap.items():
            valueElement = element.find(xpath,namespaces)
            if valueElement is not None:
                setattr(self,prop,valueElement.text)
                self._props.append(prop)
        pass        
    
    def __str__(self):
        text=""
        for prop in self._props:
            text=f"{text}{prop}:{getattr(self,prop)}\n"
        return text
    
class XMLEntityParser():
    '''
    a parser for XML Entities
    '''
    def __init__(self,filePath:str,recordsTag:str):
        '''
        Constructor
        
        Args:
            filePath(str): the path to the xml file to parse
            recordsTag(str): the name of the tag to parse
        '''
        self.filePath=filePath
        self.recordsTag=recordsTag
        
    def readXmlFile(self) -> Iterator[Element]:
        """Reads an XML file element by element and returns an iterator of either dicts or XML elements"""
        with open(self.filePath, 'rb') as xml_file:
            context = ElementTree.iterparse(xml_file, events=('start', 'end',))
            context = iter(context)
            root = None
    
            for event, element in context:
                if root is None:
                    root = element
    
                if event == 'end' and element.tag == self.recordsTag:
                    yield element
                    # clear the root element to leave it empty and use less memory
                    if root != element:
                        root.clear()
        
    def parse(self,xmlPropertyMap:dict,namespaces:dict)-> Iterator[XmlEntity]:
        '''
        parse my file
        
        Args:
            xmlPropertyMap(dict): attribute/xpath expression dict
            namespaces(dict): namespace / namespace path dict 
        '''
        try:
            for element in self.readXmlFile():
                yield XmlEntity(element,xmlPropertyMap,namespaces)
        except ParseError as parseError:
            print (f"parse error in {self.filePath}:{parseError}")
            pass


class DROPS(object):
    '''
    access to Dagstuhl research online publication server
    
    '''

    def __init__(self,maxCollectionId:int):
        '''
        Constructor
        
        Args: 
          maxCollectionId(int): the maximum collectionId currently published in DROPS
        '''
        self.maxCollectionId=maxCollectionId
        home = path.expanduser("~")
        self.cachedir= f"{home}/.conferencecorpus/drops"
        if not os.path.exists(self.cachedir):
            os.makedirs(self.cachedir)
        
    def xmlFilepath(self,collectionId):
        '''
        get my xmlFilepath
        
        Returns:
            str: the path to my xml file in the cache directory
        '''
        xmlp=f"{self.cachedir}/{collectionId}.xml"
        return xmlp
    
    def showProgress(self,collectionId,showStep=20):
        if showStep>0:
            print('.', end='')
            if collectionId % showStep ==0:
                print(f"{collectionId}",end='')  
            if collectionId % 80 ==0:
                print()    
        
    def cache(self,collectionId,baseurl="https://submission.dagstuhl.de/services/metadata/xml/collections",force:bool=False,progressStep=20):
        '''
        cache the XML file for the given collectionId
        
        Args:
            collectionId(int): the id of the volume
            baseurl(str): the base url
            force(bool): if true reload even if already cached
            progressStep(int): if > 0 show the progress with numeric display every progressStep items
        '''
      
        cfilepath=self.xmlFilepath(collectionId)
        if Download.needsDownload(cfilepath,force):
            url= f"{baseurl}/{collectionId}"
            try:
                xml=Download.getURLContent(url)
                with open(cfilepath, "w") as xmlfile:
                    xmlfile.write(xml)
            except urllib.error.HTTPError as err:
                if not "HTTP Error 404: Not Found" in str(err):
                    raise err
                 
                pass
            
        self.showProgress(collectionId,progressStep)
       
                
    def parse(self,collectionId:int,progressStep:int=200):
        '''
          parse the xml data of  volume with the given collectionId
          
          Args:
            collectionId(int): the id of the volume
            baseurl(str): the base url
            force(bool): if true reload even if already cached
            progressStep(int): if > 0 show the progress with numeric display every progressStep items
        '''    
        recordTag="{https://submission.dagstuhl.de/services/metadata/xml/dagpub.xsd}volume"
        xmlPath=self.xmlFilepath(collectionId)
        namespaces={'ns0':'https://submission.dagstuhl.de/services/metadata/xml/dagpub.xsd'}
        xmlPropertyMap= {
            "title": './ns0:title',
            "shortTitle": './ns0:shortTitle',
            "date": './ns0:date',
            "location": './ns0:location',
            'dblp': './ns0:conference/ns0:dblp',
            'website': '.ns0:conference/ns0:website'
        }        
        if os.path.exists(xmlPath):
            xmlParser=XMLEntityParser(xmlPath,recordTag)
            for xmlEntity in xmlParser.parse(xmlPropertyMap,namespaces):
                yield(xmlEntity)
            self.showProgress(collectionId,progressStep)