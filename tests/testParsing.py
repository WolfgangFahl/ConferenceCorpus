'''
Created on 2022-04-09

@author: wf
'''
from tests.basetest import BaseTest,Profiler
from pyparsing import oneOf
from ptp.parsing import Tokenizer
from ptp.signature import ParsingCategory,RegexpCategory,OrdinalCategory, EnumCategory, CountryCategory,YearCategory
from corpus.event import EventStorage

class TestParsing(BaseTest):
    
    def getEventTitles(self):
        '''
        get all Events
        '''
        sqlDB=EventStorage.getSqlDB()
        sqlQuery="select eventId,source,title from event"
        titles=sqlDB.query(sqlQuery)
        return titles
        
    """
    tests Parsing EventReferences
    """
    def testMostCommonCategories(self):
        '''
        get the most common categories
        '''
        categories=[
            RegexpCategory("first Letter",lambda word:word[0] if word else '',r".*"),
            RegexpCategory("word",lambda word:word,r".*"),
            # TODO: region, city
            OrdinalCategory(),
            YearCategory(),
            CountryCategory(),
            EnumCategory('month'),
            EnumCategory('delimiter'),
            EnumCategory('eventType'),
            EnumCategory('extract'),
            EnumCategory('field'),
            EnumCategory('frequency'),
            EnumCategory('organization'),
            EnumCategory('publish'),
            EnumCategory('scope'),
            EnumCategory('syntax'),
            ParsingCategory('part',"Part"+oneOf("A B C 1 2 3 4 I II III IV")+".")
        ]
        tokenizer=Tokenizer(categories)
        titleRows=self.getEventTitles()
        limit=50
        count=0
        for titleRow in titleRows:
            title=titleRow["title"]
            event=f"""{titleRow["source"]}-{titleRow["eventId"]}"""
            tokenSequence=tokenizer.tokenize(title,event)
            count+=1
            if count<=limit:
                for token in tokenSequence.matchResults:
                    print(token)
        show=True
        if show:
            for category in categories:
                print(f"=== {category.name} ===")
                print(category.mostCommonTable(tablefmt="mediawiki"))