'''
Created on 2021-01-25

@author: wf
'''
import unittest
from dblp.dblpxml import Dblp
from lodstorage.schema import SchemaManager
from datetime import datetime
import time
#import logging
from lodstorage.sql import SQLDB
from lodstorage.uml import UML

class TestDblp(unittest.TestCase):
    '''
    test the dblp xml parser and pylodstorage extraction for it
    '''

    def setUp(self):
        self.debug=False
#        if self.debug:
#            logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
#        else:
#            logging.basicConfig(stream=sys.stderr, level=logging.INFO)          
#        self.logger=logging.getLogger("TestDblp")
        self.mock=True
        # uncomment for recreation
        # self.debug=True
        # self.mock=False
        pass

    def tearDown(self):
        pass
    
    def log(self,msg):
        if self.debug:
            print(msg)
            #self.logger.debug(msg)
    
    @staticmethod
    def getMockedDblp(mock=True,debug=False):
        dblp=Dblp(debug=debug)
        if mock:
            dblp.xmlpath="/tmp/dblp"
            dblp.gzurl="http://wiki.bitplan.com/images/confident/dblp.xml.gz"
            dblp.reinit()
        xmlfile=dblp.getXmlFile()
        if debug:
            print("dblp xml file is  %s with size %5.1f MB" % (xmlfile,dblp.getSize()/1024/1024))
        return dblp
        
    def getDblp(self):
        '''
        get the dblp 
        '''
        dblp=TestDblp.getMockedDblp(self.mock,debug=self.debug)
        return dblp
    
    def getSqlDB(self,recreate=False):
        dblp=self.getDblp()
        limit=10000 if self.mock else 10000000
        progress=1000 if self.mock else 100000
        sample=5
        sqlDB=dblp.getSqlDB(limit, progress=progress, sample=sample, debug=self.debug,recreate=recreate,postProcess=dblp.postProcess)
        return sqlDB
    
    def testDblpDownload(self):
        '''
        test dblp access
        '''
        dblp=self.getDblp()
        minsize=988816 if self.mock else 3099271450
        self.assertTrue(dblp.isDownloaded(minsize=minsize))
        pass
    
    def testCreateSample(self):
        '''
        test creating a sample file
        '''
        #self.mock=False
        dblp=self.getDblp()
        sampletree=dblp.createSample()
        records=len(sampletree.getroot().getchildren())
        self.log("sample has %d records" % records)
        samplefile="/tmp/dblpsample.xml"
        with open(samplefile,'wb') as f:
            sampletree.write(f,encoding='UTF-8')
    
    def testDblpXmlParser(self):
        '''
        test parsing the xml file
        '''
        dblp=self.getDblp()
        xmlfile=dblp.getXmlFile()
        self.assertTrue(xmlfile is not None)
        index=0
        starttime=time.time()
        if self.debug:
            showProgressAt=500000
        else:
            showProgressAt=5000000
        for _, elem in dblp.iterParser():
            index+=1
            if index%showProgressAt==0:
                elapsed=time.time()-starttime
                print ("%8d: %5.1f s %5.0f/s %s" % (index,elapsed,index/elapsed,elem))
            dblp.clear_element(elem)    
        expectedIndex=35000 if self.mock else 70000000
        self.assertTrue(index>expectedIndex)
        
    def checkConfColumn(self,sqlDB):
        tableDict=sqlDB.getTableDict()
        self.assertTrue("proceedings in tableDict")
        proceedingsTable=tableDict["proceedings"]
        pcols=proceedingsTable["columns"]
        self.assertTrue("conf" in pcols)
        
    def testSqlLiteDatabaseCreation(self):
        '''
        get  dict of list of dicts (tables)
        '''
        sqlDB=self.getSqlDB(recreate=True)
        tableList=sqlDB.getTableList()
        expected=6 if self.mock else 8
        self.assertEqual(expected,len(tableList))
        self.checkConfColumn(sqlDB)
        sqlDB.close()
        
    def testParameterizedQuery(self):
        '''
        test the parameterized query
        '''
        dblp=self.getDblp()
        dblp.getXmlFile(reload=True)
        sqlDB=self.getSqlDB(recreate=self.mock)
        self.checkConfColumn(sqlDB)
        query="select * from proceedings where conf=?"
        records=sqlDB.query(query,('iccv',))
        self.log("found %d iccv records" % len(records))
        self.assertTrue(len(records)>=19)
            
    def testUml(self):
        '''
        test generating the uml diagram for the entities
        '''
        #self.mock=False
        dblp=self.getDblp()
        dbname="%s/%s" % (dblp.xmlpath,"dblp.sqlite")
        sqlDB=SQLDB(dbname)
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