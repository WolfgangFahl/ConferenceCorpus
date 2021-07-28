'''
Created on 2021-01-25

@author: wf
'''
from pathlib import Path
from io import BytesIO
import urllib.request
from gzip import GzipFile
from lxml import etree
from collections import Counter
from xml.dom import minidom
from lodstorage.sql import SQLDB
from lodstorage.schema import Schema
import os
import re
import time

class Dblp(object):
    '''
    handler for https://dblp.uni-trier.de/xml/ dumps
    see https://github.com/IsaacChanghau/DBLPParser/blob/master/src/dblp_parser.py
    '''

    def __init__(self,xmlname:str="dblp.xml",dtd_validation:bool=False,xmlpath:str=None,gzurl:str="https://dblp.uni-trier.de/xml/dblp.xml.gz",debug=False,verbose=True):
        '''
        Constructor
        
        Args:
            xmlname (str): name of the xml file
            dtd_validation (bool): True if dtd validation should be activated when parsing
            xmlpath(str): download path
            gzurl(str): url of the gzipped original file
            debug(bool): if True show debugging information
            verbose(bool): if True show logging information
        '''
        self.debug=debug
        self.verbose=verbose
        if xmlpath is None:
            home = str(Path.home())
            xmlpath="%s/.dblp" % home
        self.gzurl=gzurl
        self.xmlname=xmlname
        self.xmlpath=xmlpath
        self.dtd_validation=dtd_validation
        self.reinit()
        
    def reinit(self):
        '''
        reinitialize my file names
        '''
        self.xmlfile="%s/%s" % (self.xmlpath,self.xmlname)
        self.dtdfile="%s/%s" % (self.xmlpath,self.xmlname.replace(".xml",".dtd"))
     
    def getSize(self):
        '''
        get the size of my xmlFile
        
        Returns:
            the size 
        '''
        stats=os.stat(self.xmlfile)
        size=stats.st_size
        return size
           
    def isDownloaded(self,minsize:int=3000000000)->bool:
        '''
        check that the dblp file is downloaded
        
        Returns:
            bool: True if the dblpfile is fully downloaded and is bigger than the given minimum size
        '''
        result=os.path.isfile(self.xmlfile)
        if result:
            result=self.getSize()>=minsize
        return result
    
    def prettyXml(self,tree,indent='  '):
        xmlstr = minidom.parseString(etree.tostring(tree.getroot())).toprettyxml(indent=indent)
        return xmlstr
    
    def createSample(self,keyEntities=None,keyPrefix="conf/",entityLimit=1000,entities=None,progress:int=500000):
        '''
        create a sample with the given entityLimit
        
        Args:
            keyPrefix(str): the keyPrefix to filter for
        '''
        if entities is None:
            entities=['article','book','incollection','www']
        if keyEntities is None:
            keyEntities=['proceedings','inproceedings']
        allEntities=[]
        allEntities.extend(entities)
        allEntities.extend(keyEntities)
        root = etree.Element('dblp')
        counter=Counter()
        level=0
        count=0
        for event, element in self.iterParser():
            count+=1
            if progress is not None:
                if count%progress==0:
                    print(".",flush=True,end='')
                if count%(progress*80)==0:
                    print("\n",flush=True)
            if event == 'start': 
                level += 1;
                if level==2:
                    doadd=element.tag in entities
                    if element.tag in keyEntities:
                        if 'key' in element.attrib:
                            key=element.attrib['key']
                            if key.startswith(keyPrefix):
                                doadd=True
                    if (doadd and counter[element.tag]<entityLimit):
                        node=etree.fromstring(etree.tostring(element))
                        root.append(node)
                        counter[element.tag]+=1
                    else:
                        keys=counter.keys()
                        done=True
                        for entity in allEntities:
                            if not entity in keys:
                                done=False
                            else:
                                done=done and counter[entity]>=entityLimit
                        if done:
                            break
                        
                pass
            elif event == 'end':
                level -=1;
            self.clear_element(element)
        sampleTree=etree.ElementTree(root) 
        return sampleTree
        
    def getXmlFile(self,reload=False):
        '''
        get the dblp xml file - will download the file if it doesn't exist
        
        Args:
            reload(bool): if True force download
        Returns:
            str: the xmlfile
        '''
        if not os.path.isfile(self.xmlfile) or reload:
            os.makedirs(self.xmlpath,exist_ok=True)
            if self.verbose:
                print("downloading %s from %s" % (self.xmlfile, self.gzurl))
            urlreq = urllib.request.urlopen(self.gzurl)
            z = GzipFile(fileobj=BytesIO(urlreq.read()), mode='rb')
            with open(self.xmlfile, 'wb') as outfile:
                outfile.write(z.read())
        if not os.path.isfile(self.dtdfile) or reload:
            dtdurl=self.gzurl.replace(".xml.gz",".dtd")
            urllib.request.urlretrieve (dtdurl, self.dtdfile)
        
        return self.xmlfile
    
    def iterParser(self):
        """
           Create a dblp data iterator of (event, element) pairs for processing
           Returns:
               etree.iterparse result
        """
        if not os.path.isfile(self.xmlfile):
            raise ("dblp xml file %s not downloaded yet - please call getXmlFile first")
        # with dtd validation
        if self.debug:
            print("starting parser for %s " % self.xmlfile)
        return etree.iterparse(source=self.xmlfile, events=('end', 'start' ), dtd_validation=self.dtd_validation, load_dtd=True)  
    
    def clear_element(self,element):
        """
        Free up memory for temporary element tree after processing the element
        
            Args:
                element(node): the etree element to clear together with it's parent
        """
        element.clear()
        while element.getprevious() is not None:
            del element.getparent()[0]
            
    def postProcess(self,kind,index,row):
        '''
        postProcess the given row
        '''
        if 'key' in row:
            key=row['key']
            if key.startswith("conf/"):
                conf=re.sub(r"conf/(.*)/.*",r"\1",key)
                row['conf']=conf
        pass
    
    def getXmlSqlDB(self,reload=False):
        self.getXmlFile(reload=reload)
        return self.getSqlDB(postProcess=self.postProcess)
        
            
    def getSqlDB(self,limit=1000000000,progress=100000,sample=None,createSample=10000000,debug=False,recreate=False,postProcess=None,check_same_thread=False):
        '''
        get the SQL database or create it from the XML content
        '''
        dbname="%s/%s" % (self.xmlpath,"dblp.sqlite")
        if sample is None:
            sample=5
        if (os.path.isfile(dbname)) and not recreate:
            sqlDB=SQLDB(dbname=dbname,debug=debug,errorDebug=True,check_same_thread=check_same_thread)
        else:
            if (os.path.isfile(dbname)) and recreate:
                os.remove(dbname)
            sqlDB=SQLDB(dbname=dbname,debug=debug,errorDebug=True,check_same_thread=check_same_thread)
            starttime=time.time()
            dictOfLod=self.asDictOfLod(limit,progress=progress)
            elapsed=time.time()-starttime
            executeMany=True;
            fixNone=True    
            for i, (kind, lod) in enumerate(dictOfLod.items()):
                if postProcess is not None:
                    for j,row in enumerate(lod):
                        postProcess(kind,j,row)
            for i, (kind, lod) in enumerate(dictOfLod.items()):
                if debug:
                    print ("#%4d %5d: %s" % (i+1,len(lod),kind))
                entityInfo=sqlDB.createTable(lod,kind,'key',sampleRecordCount=createSample,failIfTooFew=False)
                sqlDB.store(lod,entityInfo,executeMany=executeMany,fixNone=fixNone)
                for j,row in enumerate(lod):
                    if debug:
                        print ("  %4d: %s" % (j,row)) 
                    if j>sample:
                        break
            if debug:
                print ("%5.1f s %5d rows/s" % (elapsed,limit/elapsed))
            tableList=sqlDB.getTableList()     
            viewDDL=Schema.getGeneralViewDDL(tableList, "record")
            if debug:
                print(viewDDL)
            sqlDB.execute(viewDDL)
        return sqlDB
            
    def asDictOfLod(self,limit:int=1000,delim:str=',',progress:int=None):
        '''
        get the dblp data as a dict of list of dicts - effectively separating the content
        into table structures
        
        Args:
            limit(int): maximum amount of records to process
            delim(str): the delimiter to use for splitting attributes with multiple values (e.g. author)
            progress(int): if set the interval at which to print a progress dot 
        '''
        index=0
        count=0
        level=0
        dictOfLod={}
        current={}
        for event, elem in self.iterParser():
            if event == 'start': 
                level += 1;
                if level==2:
                    kind=elem.tag
                    if not kind in dictOfLod:
                        dictOfLod[kind]=[]
                    lod=dictOfLod[kind]
                    if hasattr(elem, "attrib"):
                        current = {**current, **elem.attrib}
                elif level==3:
                    if elem.tag in current:
                        current[elem.tag]="%s%s%s" % (current[elem.tag],delim,elem.text)
                    else:
                        current[elem.tag]=elem.text    
            elif event == 'end':
                if level==2:
                    lod.append(current)
                    count+=1
                    current={} 
                    if progress is not None:
                        if count%progress==0:
                            print(".",flush=True,end='')
                        if count%(progress*80)==0:
                            print("\n",flush=True)
                    if count>=limit:
                        break
                level -= 1;
            index+=1
            self.clear_element(elem)
        return dictOfLod
            
        
    