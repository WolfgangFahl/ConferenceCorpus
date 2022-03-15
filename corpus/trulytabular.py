'''
Created on 2022-04-14

@author: wf
'''
from lodstorage.sparql import SPARQL
from lodstorage.query import Query,QueryManager
import os
import re


class WikidataProperty():
    '''
    a WikidataProperty
    '''
    
    def __init__(self,pid:str):
        '''
        construct me with the given property id
        
        Args:
            pid(str): the property Id
        '''
        self.pid=pid
        self.reverse=False
    
    def getPredicate(self):
        '''
        get me as a Predicate
        '''
        reverseToken="^" if self.reverse else ""
        pLabel=f"{reverseToken}wdt:{self.pid}"
        return pLabel
    
    def __str__(self):
        text=self.pid
        if hasattr(self, "label"):
            text=f"{self.label} ({self.pid})"
        return text
      
    @classmethod
    def getPropertiesByLabels(cls,sparql,propertyLabels:list,lang:str="en"):
        '''
        get a list of Wikidata properties by the given label list
        
        Args:
            sparql(SPARQL): the SPARQL endpoint to use
            propertyLabels(list): a list of labels of the property
            lang(str): the language of the label
        '''
        # the result dict
        wdProperties={}
        valueClause=""
        for propertyLabel in propertyLabels:
            valueClause+=f'   "{propertyLabel}"@{lang}\n'
        query="""
# get the property for the given labels
SELECT ?property ?propertyLabel WHERE {
  VALUES ?propertyLabel {
%s
  }
  ?property rdf:type wikibase:Property;
  rdfs:label ?propertyLabel.
  FILTER((LANG(?propertyLabel)) = "en")
}""" % valueClause
        qLod=sparql.queryAsListOfDicts(query)
        for record in qLod:
            url=record["property"]
            pid=re.sub(r"http://www.wikidata.org/entity/(.*)",r"\1",url)
            prop=WikidataProperty(pid)
            prop.pLabel=record["propertyLabel"]
            prop.url=url
            wdProperties[prop.pLabel]=prop
            pass
        return wdProperties
        

class TrulyTabular(object):
    '''
    truly tabular RDF analysis
    '''

    def __init__(self, itemQid, propertyLabels:list=[], endpoint="https://query.wikidata.org/sparql",lang="en",debug=False):
        '''
        Constructor
        
        Args:
            itemQid: wikidata id of the type to analyze 
        '''
        self.itemQid=itemQid
        self.debug=debug
        self.endpoint=endpoint
        self.sparql=SPARQL(endpoint)
        self.lang=lang
        self.label=self.getLabel(itemQid,lang=self.lang)
        self.queryManager=TrulyTabular.getQueryManager(debug=self.debug)
        self.properties=WikidataProperty.getPropertiesByLabels(self.sparql, propertyLabels, lang)
        
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
        
    def getLabel(self,itemId:str,lang:str="en"):
        '''
        get  the label for the given item
        
        Args:
            itemId(str): the wikidata Q/P id
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
}""" % (itemId,lang)
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
    
    def noneTabularQuery(self,wdProperty:WikidataProperty,asFrequency:bool=True):
        '''
        get the none tabular entries for the given property
        
        Args:
            wdProperty(WikidataProperty): the property to analyze
            asFrequency(bool): if true do a frequency analysis
        '''
        propertyLabel=wdProperty.pLabel
        propertyId=wdProperty.pid
        # work around https://github.com/RDFLib/sparqlwrapper/issues/211
        if "described at" in propertyLabel:
            propertyLabel=propertyLabel.replace("described at","describ'd at")
        sparql=f"""
# Count all {self.asText(long=True)} items
# with the given {propertyLabel}({propertyId}) https://www.wikidata.org/wiki/Property:{propertyId} 
SELECT ?item ?itemLabel (COUNT (?value) AS ?count)
WHERE
{{
  # instance of {self.label}
  ?item wdt:P31 wd:{self.itemQid}.
  ?item rdfs:label ?itemLabel.
  filter (lang(?itemLabel) = "en").
  # {propertyLabel}
  ?item {wdProperty.getPredicate()} ?value.
}} GROUP by ?item ?itemLabel
"""
        if asFrequency:
            freqDesc="frequencies"
            sparql=f"""SELECT ?count (COUNT(?count) AS ?frequency) WHERE {{
{sparql}
}}
GROUP BY ?count
ORDER BY DESC (?frequency)"""
        else:
            freqDesc="records"
            sparql=f"""{sparql}
HAVING (COUNT (?value) > 1)
ORDER BY DESC(?count)"""
        query=Query(query=sparql,name=f"NonTabular {self.label}/{propertyLabel}:{freqDesc}",title=f"non tabular entries for {self.label}/{propertyLabel}:{freqDesc}")
        return query

    def noneTabular(self,wdProperty:WikidataProperty):
        '''
        get the none tabular result for the given Wikidata property
        
        Args:
            wdProperty(WikidataProperty): the Wikidata property
        '''
        query=self.noneTabularQuery(wdProperty)
        if self.debug:
            print(query.query)
        qlod=self.sparql.queryAsListOfDicts(query.query)
        return qlod
    
    def addStatsColWithPercent(self,m,col,value,total): 
        '''
        add a statistics Column
        '''
        m[col]=value
        m[f"{col}%"]=f"{value/total*100:.1f}"
    
    def getPropertyStatics(self):
        '''
        get the property Statistics
        '''
        itemCount=self.count()
        lod=[{
            "property": "∑",
            "total": itemCount
        }]
        for wdProperty in self.properties.values():
            ntlod=self.noneTabular(wdProperty)
            statsRow={"property":wdProperty.pLabel}
            total=0
            nttotal=0
            for record in ntlod:
                f=record["frequency"]
                count=record["count"]
                statsRow[f"f{count}"]=f
                if count>1:
                    nttotal+=f
                total+=f
                self.addStatsColWithPercent(statsRow,"total",total,itemCount)
                self.addStatsColWithPercent(statsRow,"non tabular",nttotal,total)
            lod.append(statsRow)
        return lod
    

        