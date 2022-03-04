'''
Created on 2022-03-03

@author: wf
'''
from corpus.datasources.download import Download
from os import path
import os
import urllib
from corpus.xml.xmlparser import XMLEntityParser


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