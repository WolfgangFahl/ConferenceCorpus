'''
Created on 2022-04-11

@author: wf
'''
from pyparsing import oneOf
from ptp.parsing import Tokenizer
from ptp.signature import ParsingCategory, RegexpCategory, OrdinalCategory, EnumCategory, CountryCategory, YearCategory, \
    VolumeCategory, CityPrefixCategory, CityCategory, AcronymCategory


class EventReferenceParser(object):
    '''
    given an Event reference returns the signature with probabilities
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.categories=[
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
            ParsingCategory('part',"Part"+oneOf("A B C 1 2 3 4 I II III IV")+"."),
            VolumeCategory(),
            CityPrefixCategory(),
            CityCategory(),
            AcronymCategory()
        ]
        self.tokenizer=Tokenizer(self.categories)
        
    def parse(self,eventReference:str,eventContext:object,show:bool=True):
        '''
        parse the given eventReference for the given eventContext
        
        Args:
            eventReference(str): a reference for an event
            eventContext(object): the object this reference is referencing
            show(bool): if True show the parse result
        '''
        tokenSequence=self.tokenizer.tokenize(eventReference,eventContext)
        if show:
            for token in tokenSequence.matchResults:
                print(token)
        return tokenSequence
        
    def showStatistics(self,tablefmt="mediawiki"):
        '''
        show the statistics in the given table format
        '''
        for category in self.categories:
            print(f"=== {category.name} ===")
            print(category.mostCommonTable(tablefmt=tablefmt))
            
    def lookupToYaml(self,lookup,name:str,tables:list,yamlPath:str,show:bool=True):
        '''
        save the given lookup dictionary as a yamlfile
        
        Args:
            lookup(dict): the lookup dictionary
            name(str): the name of the dictionary
            tables(list): the source tables this lookup is created from
            yamlPath(str): the path where to store the dictionary
            show(bool): if True show details before saving
        '''
        if show:
            print(f"found {len(lookup)} {name}")
        yamlstr=f"""# lookup for {name}
# created from {len(lookup)} {name} 
# analyzed from the sources {tables}
"""
        for entry in lookup:
            d=lookup[entry]
            yamlstr+=f"""{d["name"]}:
    qid: {d["qid"]}
    frequency: {d["frequency"]}\n"""
            for table in tables:
                if table in d:
                    yamlstr+=f"    {table}: {d[table]}\n"
        yamlFile=f"{yamlPath}/{name}.yaml"
        print(yamlstr,  file=open(yamlFile, 'w'))
        