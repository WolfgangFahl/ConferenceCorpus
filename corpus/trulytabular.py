'''
Created on 2022-04-14

@author: wf
'''
from lodstorage.sparql import SPARQL
from lodstorage.query import QueryManager
import os

class TrulyTabular(object):
    '''
    truly tabular RDF analysis
    '''

    def __init__(self, itemQid, endpoint="https://query.wikidata.org/sparql",debug=False):
        '''
        Constructor
        
        Args:
            itemQid: wikidata id of the type to analyze 
        '''
        self.itemQid=itemQid
        self.debug=debug
        self.endpoint=endpoint
        self.sparql=SPARQL(endpoint)
        self.label=self.getLabel(itemQid)
        self.queryManager=TrulyTabular.getQueryManager(debug=self.debug)
        
    def __str__(self):
        return self.asText(long=False)
    
    @classmethod
    def getQueryManager(cls,lang='sparql',name="trulytabular",debug=False):
        '''
        get the query manager for the given language and fileName
        
        Args:
            lang(str): the language of the queries to extract
            name(str): the name of the manager containing the query specifications
            debug(bool): if True set debugging on
        '''
        scriptDir=os.path.dirname(__file__)
        for path in [f"{scriptDir}/../resources"]:
            qYamlFile=f"{path}/{name}.yaml"
            if os.path.isfile(qYamlFile):
                qm=QueryManager(lang=lang,debug=debug,queriesPath=qYamlFile)
                return qm
        return None
    
    def asText(self,long:bool=True):
        if long:
            return f"{self.label}({self.itemQid}) https://www.wikidata.org/wiki/{self.itemQid}"
        else:
            return f"{self.label}({self.itemQid})"
        
    def getValue(self,query:str,attr:str):
        '''
        get the value for the given Query using the given attr
        
        Args:
            query(str): the SPARQL query to run
            attr(str): the attribute to get
        '''
        if self.debug:
            print(query)
        qLod=self.sparql.queryAsListOfDicts(query)
        return self.getFirst(qLod, attr)
        
    def getFirst(self,qLod:list,attr:str):
        '''
        get the 
        '''
        if len(qLod)==1 and attr in qLod[0]:
            return qLod[0][attr]
        raise Exception(f"getFirst for attribute {attr} failed for {qLod}")
        
    def getLabel(self,itemQid:str,lang:str="en"):
        '''
        get  the label for the given item
        
        Args:
            itemQid(str): the wikidata Q id
            lang(str): the language of the label
        '''
        query="""
# get the label for the given item
SELECT ?itemLabel
WHERE
{
  VALUES (?item) {
    (wd:%s)
  }
  ?item rdfs:label ?itemLabel.
  filter (lang(?itemLabel) = "%s").
}""" % (itemQid,lang)
        return self.getValue(query, "itemLabel")
        
    def count(self):
        '''
        get my count
        '''
        query=f"""# Count all items with the given 
# type {self.asText(long=True)}
SELECT (COUNT (DISTINCT ?item) AS ?count)
WHERE
{{
  # instance of {self.label}
  ?item wdt:P31 wd:{self.itemQid}.
}}"""
        return self.getValue(query, "count")
    
    def mostFrequentIdentifiersQuery(self):
        '''
        get the most frequently used identifiers
        '''
        query=self.queryManager.queriesByName["mostFrequentIdentifiers"]
        query.title=f"most frequently used identifiers for {self.asText(long=True)}"
        query.query=query.query % self.itemQid
        return query
    
    def noneTabular(self,propertyId:str,propertyLabel:str,reverse:bool=False):
        '''
        get the none tabular entries for the given property
        
        Args:
            propertyId(str): the property id e.g. P276
            propertyLabel(str): the property label e.g. location
        '''
        if reverse: 
            reverse="^" 
        else: 
            reverse=""
        query=f"""
# Count all {self.asText(long=True)} items
# with the given {propertyLabel}({propertyId}) https://www.wikidata.org/wiki/Property:{propertyId} 
SELECT ?item (COUNT (?value) AS ?count)
WHERE
{{
  # instance of {self.label}
  ?item wdt:P31 wd:{self.itemQid}.
  # {propertyLabel}
  ?item {reverse}wdt:{propertyId} ?value.
}} GROUP by ?item
HAVING (COUNT (?value) > 1)
ORDER BY DESC(?count)"""
        if self.debug:
            print(query)
        qlod=self.sparql.queryAsListOfDicts(query)
        return qlod

        