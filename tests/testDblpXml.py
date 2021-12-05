'''
Created on 2021-01-25

@author: wf
'''
import unittest

from corpus.datasources.dblpxml import DblpXml
from lodstorage.schema import SchemaManager
from datetime import datetime
import os
import time
#import logging
from lodstorage.uml import UML
import getpass

class TestDblp(unittest.TestCase):
    '''
    test the dblp xml parser and pylodstorage extraction for it
    '''
    mock=True
    
    def setUp(self):
        '''
        setUp the test environment 
        
        especically the mocking parameter - if mock is  False a multi-Gigabyte download
        might be activated
        '''
        self.debug=False
        self.verbose=True
        self.mock=TestDblp.mock
#        if self.debug:
#            logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
#        else:
#            logging.basicConfig(stream=sys.stderr, level=logging.INFO)          
#        self.logger=logging.getLogger("TestDblp")   
        pass

    def tearDown(self):
        pass
    
    @staticmethod
    def inCI():
        '''
        are we running in a Continuous Integration Environment?
        '''
        publicCI=getpass.getuser() in ["travis", "runner"] 
        jenkins= "JENKINS_HOME" in os.environ;
        return publicCI or jenkins
    
    def log(self,msg):
        if self.debug:
            print(msg)
            #self.logger.debug(msg)
    
    @staticmethod
    def getMockedDblp(mock=True,debug=False):
        dblpXml=DblpXml(debug=debug)
        if mock:
            dblpXml.xmlpath="/tmp/dblp"
            dblpXml.gzurl="https://github.com/WolfgangFahl/ConferenceCorpus/wiki/data/dblpsample.xml.gz"
            dblpXml.reinit()
        xmlfile=dblpXml.getXmlFile()
        sizeMB=dblpXml.getSize()/1024/1024
        if debug or not mock:
            print(f"dblp xml file is  {xmlfile} with size {sizeMB:5.1f} MB" )
        return dblpXml
    
    def getSqlDB(self,mock=True,recreate=False):
        '''
        get the Sql Database
        '''
        dblpXml=self.getMockedDblp(mock=mock)
        limit=10000 if mock else 10000000
        showProgress=not mock  and not self.inCI()
        sample=5
        sqlDB=dblpXml.getSqlDB(limit, sample=sample, debug=self.debug,recreate=recreate,postProcess=dblpXml.postProcess,showProgress=showProgress)
        return sqlDB
    
    def testDblpDownload(self):
        '''
        test dblp access
        '''
        isMocked=TestDblp.mock
        dblp=self.getMockedDblp(mock=isMocked)
        minsize=988816 if isMocked else 3099271450
        self.assertTrue(dblp.isDownloaded(minsize=minsize))
        pass
    
    def testCreateSample(self):
        '''
        test creating a sample file
        '''
        #isMocked=TestDblp.mock
        #self.debug=True
        dblpXml=self.getMockedDblp()
        sampletree=dblpXml.createSample()
        records=len(sampletree.getroot().getchildren())
        self.log(f"sample has {records} records")
        samplefile="/tmp/dblpsample.xml"
        with open(samplefile,'wb') as f:
            sampletree.write(f,encoding='UTF-8')
    
    def testDblpXmlParser(self):
        '''
        test parsing the xml file
        '''
        isMocked=True
        dblpXml=self.getMockedDblp()
        xmlfile=dblpXml.getXmlFile()
        self.assertTrue(xmlfile is not None)
        index=0
        starttime=time.time()
        if self.debug:
            showProgressAt=500000
        else:
            showProgressAt=5000000
        for _, elem in dblpXml.iterParser():
            index+=1
            if index%showProgressAt==0:
                elapsed=time.time()-starttime
                print ("%8d: %5.1f s %5.0f/s %s" % (index,elapsed,index/elapsed,elem))
            dblpXml.clear_element(elem)    
        expectedIndex=35000 if isMocked else 70000000
        self.assertTrue(index>expectedIndex)
        
    def checkConfColumn(self,sqlDB):
        '''
        check the conference columns
        '''
        tableDict=sqlDB.getTableDict()
        self.assertTrue("proceedings in tableDict")
        proceedingsTable=tableDict["proceedings"]
        pcols=proceedingsTable["columns"]
        self.assertTrue("conf" in pcols)
        
    def testSqlLiteDatabaseCreation(self):
        '''
        get  dict of list of dicts (tables)
        '''
        mock=self.mock
        #mock=False
        if not mock:
            return
        sqlDB=self.getSqlDB(mock=mock,recreate=True)
        tableList=sqlDB.getTableList()
        expected=6 if self.mock else 8
        self.assertEqual(expected,len(tableList))
        self.checkConfColumn(sqlDB)
        sqlDB.close()
        
    def testIssue5(self):
        '''
        https://github.com/WolfgangFahl/ConferenceCorpus/issues/5
        
        dblp xml parser skips some proceedings titles
        
        '''
        xml="""<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE dblp SYSTEM "dblp.dtd">
<dblp><proceedings mdate="2019-05-14" key="conf/pfe/2001">
<editor>Frank van der Linden 0001</editor>
<title>Software Product-Family Engineering, 4th International Workshop, PFE 2001, Bilbao, Spain, October 3-5, 2001, Revised Papers</title>
<booktitle>PFE</booktitle>
<series href="db/series/lncs/index.html">Lecture Notes in Computer Science</series>
<volume>2290</volume>
<publisher>Springer</publisher>
<year>2002</year>
<isbn>3-540-43659-6</isbn>
<ee>https://doi.org/10.1007/3-540-47833-7</ee>
<url>db/conf/pfe/pfe2001.html</url>
</proceedings>
<proceedings mdate="2019-01-26" key="conf/hpcasia/2019">
<title>Proceedings of the International Conference on High Performance Computing in Asia-Pacific Region, HPC Asia 2019, Guangzhou, China, January 14-16, 2019</title>
<publisher>ACM</publisher>
<booktitle>HPC Asia</booktitle>
<year>2019</year>
<isbn>978-1-4503-6632-8</isbn>
<ee>https://dl.acm.org/citation.cfm?id=3293320</ee>
<url>db/conf/hpcasia/hpcasia2019.html</url>
</proceedings>
<proceedings mdate="2020-03-27" key="journals/corr/OrchardY16a">
<editor orcid="0000-0002-7058-7842">Dominic A. Orchard</editor>
<editor orcid="0000-0002-3925-8557">Nobuko Yoshida</editor>
<title>Proceedings of the Ninth workshop on Programming Language Approaches to Concurrency- and Communication-cEntric Software, PLACES 2016, Eindhoven, The Netherlands, 8th April 2016.</title>
<booktitle>PLACES</booktitle>
<year>2016</year>
<series href="db/series/eptcs/index.html">EPTCS</series>
<volume>211</volume>
<url>db/series/eptcs/eptcs211.html</url>
<ee type="oa">https://doi.org/10.4204/EPTCS.211</ee>
<ee type="oa">http://arxiv.org/abs/1606.05403</ee>
</proceedings>
</dblp>"""
        xmlname="dblptitleempty.xml"
        xmlpath="/tmp"
        with open(f"{xmlpath}/{xmlname}", 'w') as xmlfile:
            xmlfile.write(xml)
        dblpXml=DblpXml(xmlname=xmlname,xmlpath=xmlpath)
        dictOfLod=dblpXml.asDictOfLod()
        self.assertTrue("proceedings" in dictOfLod)
        procs=dictOfLod["proceedings"]
        self.assertEqual(3,len(procs))
        self.assertTrue(procs[0]["title"].startswith("Software Product-Family Engineering"))
        
        
    def testQueries(self):
        '''
        test the parameterized query
        '''
        sqlDB=self.getSqlDB(mock=TestDblp.mock,recreate=self.mock)
        self.checkConfColumn(sqlDB)
        
        query="select * from proceedings where conf=?"
        records=sqlDB.query(query,('iccv',))
        self.log("found %d iccv records" % len(records))
        self.assertTrue(len(records)>=19)
        
        query="select key,conf,booktitle,title from proceedings where title is null"
        records=sqlDB.query(query)
        if len(records)>0:
            for record in records:
                if self.debug:
                    print(record)
        if len(records)>0:
            print("Warning https://github.com/WolfgangFahl/ConferenceCorpus/issues/5 dblp xml parser skips some proceedings titles#5 is not fixed yet!")
        #self.assertEqual(0,len(records))
            
    def testUml(self):
        '''
        test generating the uml diagram for the entities
        '''
        sqlDB=self.getSqlDB(mock=TestDblp.mock,recreate=self.mock)
        uml=UML()
        now=datetime.now()
        nowYMD=now.strftime("%Y-%m-%d")
        title="""dblp.xml  Entities
%s
[[https://dblp.org/ Copyright 2009-2021 dblp computer science bibliography]]
see also [[https://github.com/WolfgangFahl/dblpconf dblp conf open source project]]
""" %nowYMD
        tableList=sqlDB.getTableList()
        schemaDefs={
                'article': 'Article',
                'book':'Book',
                'incollection': 'In Collection',
                'inproceedings': 'In Proceedings',
                'mastersthesis': 'Master Thesis',
                'phdthesis': "PhD Thesis",
                'proceedings':'Proceedings',
                'www':'Person'
        }
        baseUrl="http://wiki.bitplan.com/index.php/Dblpconf#"
        schemaManager=SchemaManager(schemaDefs=schemaDefs,baseUrl=baseUrl)
        for table in tableList:
            table['schema']=table['name']
            countQuery="SELECT count(*) as count from %s" % table['name']
            countResult=sqlDB.query(countQuery)
            table['instances']=countResult[0]['count']
        plantUml=uml.mergeSchema(schemaManager,tableList,title=title,packageName='dblp',generalizeTo="Record")
        show=False
        if show:
            print(plantUml.replace('#/','#'))
        self.assertTrue("Record <|-- article" in plantUml)
        self.assertTrue("class Record " in plantUml)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()