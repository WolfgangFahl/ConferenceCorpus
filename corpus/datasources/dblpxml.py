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
from corpus.utils.progress import Progress
import os
import re
import time

class DblpXml(object):
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
            xmlpath=f"{home}/.dblp" 
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
     
    def getSize(self)->int:
        '''
        get the size of my xmlFile
        
        Returns:
            int: the size 
        '''
        stats=os.stat(self.xmlfile)
        size=stats.st_size
        return size
    
    def getExpectedTotal(self)->int:
        '''
        get the expected Total of records
        '''
        return self.getSize()//380
    
    def warnFullSize(self):
        '''
        warn if we are using the full dataset
        '''
        print(f"Warning - using full {self.xmlfile} dataset ~{self.getExpectedTotal()/1000000:3.1f}m records!")  
        
           
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
        '''
        get a pretty XML representation of the given etree
        '''
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
        showProgress=Progress(progress)
        for event, element in self.iterParser():
            showProgress.next()
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
                print(f"downloading {self.xmlfile} from {self.gzurl}")
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
            print(f"starting parser for {self.xmlfile}"  )
        # https://lxml.de/api/lxml.etree.iterparse-class.html
        self.parser=etree.iterparse(source=self.xmlfile, events=('end', 'start' ), dtd_validation=self.dtd_validation, load_dtd=True, huge_tree=True) 
        return self.parser 
    
    def clear_element(self,element):
        """
        Free up memory for temporary element tree after processing the element
        
            Args:
                element(node): the etree element to clear together with it's parent
        """
        element.clear()
        while element.getprevious() is not None:
            del element.getparent()[0]
        
    def checkRow(self,kind:str,index,row:dict):
        '''
        check the row content
        
        Args:
            kind(str): e.g. proceedings/article
            index(int): the index of the row
            row(dict): the row to process
        '''        
        if kind=='proceedings':
            if 'title' in row:
                title=row['title']
                if not title:
                    print(f'empty title for {index}{row}')
            else:
                print(f'missing title for {index}{row}')
              
    def postProcess(self,_kind:str,_index,row:dict):
        '''
        postProcess the given row
        
        Args:
            _kind(str): e.g. proceedings/article
            _index(int): the index of the row
            row(dict): the row to process
        '''
        if 'key' in row:
            key=row['key']
            if key.startswith("conf/"):
                conf=re.sub(r"conf/(.*)/.*",r"\1",key)
                row['conf']=conf
        pass
    
    def getXmlSqlDB(self,reload=False,showProgress=False):
        '''
        get the SqlDB derived from the XML download 
        '''
        self.getXmlFile(reload=reload)
        return self.getSqlDB(postProcess=self.postProcess,showProgress=showProgress)
        
            
    def getSqlDB(self,limit=1000000000,sample=None,createSample=10000000,debug=False,recreate=False,postProcess=None,check_same_thread=False,showProgress:bool=False):
        '''
        get the SQL database or create it from the XML content
        
        Args:
            limit(int): maximum number of records
        '''
        dbname=f"{self.xmlpath}/dblp.sqlite"
        # estimate size
        if showProgress:
            expectedTotal=self.getExpectedTotal()
            progress=expectedTotal//86
        else:
            expectedTotal=None
            progress=None
        if sample is None:
            sample=5
        if (os.path.isfile(dbname)) and not recreate:
            sqlDB=SQLDB(dbname=dbname,debug=debug,errorDebug=True,check_same_thread=check_same_thread)
        else:
            if (os.path.isfile(dbname)) and recreate:
                os.remove(dbname)
            sqlDB=SQLDB(dbname=dbname,debug=debug,errorDebug=True,check_same_thread=check_same_thread)
            starttime=time.time()
            dictOfLod=self.asDictOfLod(limit,progressSteps=progress,expectedTotal=expectedTotal)
            elapsed=time.time()-starttime
            executeMany=True;
            if showProgress:
                print(f"parsing done after {elapsed:5.1f} s ... storing ...")
            starttime=time.time()    
            fixNone=True    
            for i, (kind, lod) in enumerate(dictOfLod.items()):
                if postProcess is not None:
                    for j,row in enumerate(lod):
                        postProcess(kind,j,row)
            rows=0
            for i, (kind, lod) in enumerate(dictOfLod.items()):
                rows+=len(lod)
                if debug:
                    print ("#%4d %5d: %s" % (i+1,len(lod),kind))
                entityInfo=sqlDB.createTable(lod,kind,'key',sampleRecordCount=createSample,failIfTooFew=False)
                sqlDB.store(lod,entityInfo,executeMany=executeMany,fixNone=fixNone)
                for j,row in enumerate(lod):
                    if debug:
                        print ("  %4d: %s" % (j,row)) 
                    if j>sample:
                        break
            elapsed=time.time()-starttime        
            if showProgress:
                print (f"stored {rows} rows in {elapsed:5.1f} s {rows/elapsed:5.0f} rows/s" )
            tableList=sqlDB.getTableList()     
            viewDDL=Schema.getGeneralViewDDL(tableList, "record")
            if debug:
                print(viewDDL)
            sqlDB.execute(viewDDL)
        return sqlDB
            
    def asDictOfLod(self,limit:int=1000,delim:str=',',progressSteps:int=None,expectedTotal:int=None):
        '''
        get the dblp data as a dict of list of dicts - effectively separating the content
        into table structures
        
        Args:
            limit(int): maximum amount of records to process
            delim(str): the delimiter to use for splitting attributes with multiple values (e.g. author)
            progressSteps(int): if set the interval at which to print a progress dot 
            expectedTotal(int): the expected Total number 
        '''
        index=0
        progress=Progress(progressSteps,expectedTotal,msg="Parsing dblp xml dump",showMemory=True)
        level=0
        dictOfLod={}
        current={}
        levelCount=Counter()
        for event, elem in self.iterParser():
            if event == 'start': 
                level += 1;
                levelCount[level]+=1
                if level==2:
                    kind=elem.tag
                    if not kind in dictOfLod:
                        dictOfLod[kind]=[]
                    lod=dictOfLod[kind]
                    # copy the attributes (if any)
                    if hasattr(elem, "attrib"):
                        current = {**current, **elem.attrib}
                elif level==3:
                    name=elem.tag
                    newvalue=elem.text
                    # is there already an entry for the given name
                    if name in current:
                        oldvalue=current[name]
                        newvalue=f"{oldvalue}{delim}{newvalue}"
                    # set the name/value pair
                    current[name]=newvalue    
                    if (kind=="proceedings") and (name=="title") and (elem.text is None):
                        print(f"{elem.sourceline:6}:{elem.tag} - None text")
                        pass
                elif level>=4:
                    # interesting things happen here ...
                    # sub/sup i and so on see dblp xml faq
                    #if elem.sourceline:
                    #    print(f"{elem.sourceline:6}:{elem.tag}")
                    pass
            elif event == 'end':
                if level==2:
                    lod.append(current)
                    progress.next()
                    kind=elem.tag
                    self.checkRow(kind,progress.count,current)
                    current={} 
                    if progress.count>=limit:
                        break
                level -= 1;
                self.clear_element(elem)
                index+=1
        if self.debug:
            pass
        if progress is not None:
            progress.done()
        return dictOfLod