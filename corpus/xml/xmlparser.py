'''
Created on 2022-03-04

@author: wf
'''
from xml.etree.ElementTree import Element
from xml.etree import cElementTree as ElementTree
from xml.etree.ElementTree import ParseError
#from lxml.etree.ElementTree import ElementTree
from typing import Iterator
import sys
from corpus.utils.progress import Progress

class XmlEntity(object):
    '''
    an entity based on an XML object
    '''
    debug=False
    encoding="utf-8"
    
    def __init__(self,element:Element,xmlPropertyMap:dict,namespaces:dict):
        ''' 
        constructor
        
        Args:
            element: the element to construct me from
        '''
        self._props=[]
        if XmlEntity.debug:
            xml=ElementTree.tostring(element).decode(XmlEntity.encoding)
            # debug e.g. with http://xpather.com/
            print(xml)
            setattr(self,"rawxml",xml)
        for prop, xpath in xmlPropertyMap.items():
            attr=None
            if "@"in prop:
                propparts=prop.split("@")
                prop=propparts[0]
                attr=propparts[1]
            valueElements = element.findall(xpath,namespaces)
            if valueElements is not None and len(valueElements)>0:
                # single or multi?
                if len(valueElements)==1:
                    value=self.getValue(valueElements[0],attr) 
                else:
                    value=[]
                    for valueElement in valueElements:
                        value.append(self.getValue(valueElement,attr))
                setattr(self,prop,value)
                self._props.append(prop)
        pass        
    
    def getValue(self,element,attr:str=None):
        '''
        get the value from the element
        
        Args:
            element: the XML Node
            attr: the attribute to get the value for - if None get the text
        '''
        if attr is None:
            value=element.text
        else:
            if attr in element.attrib:
                value=element.attrib[attr]
            else:
                value=None
        return value
    
    def __str__(self):
        text=""
        for prop in self._props:
            text=f"{text}{prop}:{getattr(self,prop)}\n"
        return text
    
    def asDict(self):
        '''
        return me as a dictionary
        '''
        d={}
        for prop in self._props:
            d[prop]=getattr(self,prop)
        return d
    
class XMLEntityParser():
    '''
    a parser for XML Entities
    '''
    def __init__(self,filePath:str,recordsTag:str,progress:Progress=None):
        '''
        Constructor
        
        Args:
            filePath(str): the path to the xml file to parse
            recordsTag(str): the name of the tag to parse
            progressSteps(int): how often to show the progress of the parser
        '''
        self.filePath=filePath
        self.recordsTag=recordsTag
        self.progress=progress
        
    def readXmlFile(self) -> Iterator[Element]:
        '''
           Reads an XML file element by element and returns an iterator XML elements
           see https://github.com/sopherapps/xml_stream/blob/master/xml_stream/__init__.py 
        '''
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
                if self.progress is not None:
                    self.progress.next()
        except ParseError as parseError:
            print (f"parse error in {self.filePath}:{parseError}", file=sys.stderr)
            pass