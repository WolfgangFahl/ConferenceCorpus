'''
Created on 2022-04-09

@author: wf
'''
from tests.basetest import BaseTest,Profiler
from plp.eventrefparser import EventReferenceParser
from corpus.event import EventStorage

class TestParsing(BaseTest):
    """
    tests Parsing EventReferences
    """
    
    def getEventTitles(self,limit=None,sources=None):
        '''
        get all Events with titles directly from SQL
        '''
        signatureDB=EventStorage.getSignatureCache()
        if limit is None:
            limit=""
        else:
            limit=f" LIMIT {limit}"
        if sources is None:
            sources=""
        else:
            sources_clause=""
            delim=""
            for source in sources:
                sources_clause+=f'{delim}"{source}"'
                delim=","
            sources=f" WHERE source in ({sources_clause})"
        sqlQuery=f"SELECT eventId,source,title from event{limit}{sources}"
        titles=signatureDB.query(sqlQuery)
        return titles
    
    def testGetOrCreateSignatureDB(self):
        """
        test creating the Event SignatureDB
        """
        force=self.inPublicCI()
        signatureDB=EventStorage.getSignatureCache(profile=False, force=force)
        countRecord=signatureDB.query("select count(*) as count from event")
        debug=self.debug
        debug=True
        if debug:
            print(countRecord)
        # 1759830
        self.assertTrue(countRecord[0]["count"]>1759000)
        
    def testCreateLookup(self):
        '''
        test creating a lookup dictionary
        '''
        eParser=EventReferenceParser()
        tables=["dblp","wikidata","crossref","confref"]
        yamlPath="/tmp"
        for column,columnPlural in [("country","countries"),("city","cities"),("region","regions")]:
            lookup=EventStorage.createLookup(column,tables)
            eParser.lookupToYaml(lookup, columnPlural, tables, yamlPath,show=True)
        
    def testMostCommonCategories(self):
        '''
        get the most common categories
        '''
        eParser=EventReferenceParser()
        showLimit=50
        titleRows=self.getEventTitles(limit=showLimit)
        count=0
        for titleRow in titleRows:
            title=titleRow["title"]
            event=f"""{titleRow["source"]}-{titleRow["eventId"]}"""
            count+=1
            eParser.parse(title,event,show=count<=showLimit)
        show = not self.inPublicCI()
        if show:
            eParser.showStatistics()
