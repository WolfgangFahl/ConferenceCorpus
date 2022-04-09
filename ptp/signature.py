'''
Created on 2021-05-03

Proceedings Title signature elements
@author: wf
'''
from ptp.parsing import Category
from num2words import num2words
import re
import yaml
import pathlib
from pyparsing import ParseException

class RegexpCategory(Category):
    '''
    category defined by regular expression
    '''
    def __init__(self,name,itemFunc,pattern):
        '''
        constructor
        
        Args:
            name(str): the name of this category
            itemFunc(func): the function to use for getting values
            pattern(str): the regular expression pattern to apply
        '''
        self.pattern=pattern
        super().__init__(name,itemFunc=itemFunc)
        
    def checkMatch(self,token):
        return re.search(self.pattern, token) is not None
    
class ParsingCategory(Category):
    '''
    category defined by a PyParsing grammar
    '''
    def __init__(self,name,grammar):
        self.grammar=grammar
        itemFunc=self.getResult
        super().__init__(name,itemFunc=itemFunc)
    
    def getResult(self):
        pass
        return None
    
    def checkMatch(self,token):
        self.parseResult=None
        try:
            self.parseResult=self.grammar.parseString(token)
            pass
        except ParseException as _pe:
            # ignore any parse exception
            pass
        return self.parseResult is not None
        
  
class EnumCategory(Category):
    '''
    category defined by an enumeration specified in a lookup table
    '''
   
    def getYamlPath(self,lookupName:str=None):
        '''
        get the YamlPath for the given filename prefix
        
        Args:
            filename(str): the prefix of the filename to get the Yaml path for
            
        Returns:
            str: the string representation of the path
        '''
        if lookupName is None:
            lookupName="dictionary"
        grandParent = pathlib.Path(__file__).parent.parent.resolve()
        filepath = (grandParent / f"resources/{lookupName}.yaml")
        path=str(filepath)
        return path
  
    def read(self, yamlPath=None):
        ''' read the dictionary from the given yaml path
            https://github.com/WolfgangFahl/ProceedingsTitleParser/blob/7e52b4e3eae09269464669fe387425b9f6392952/ptp/titleparser.py#L456
        '''
        if yamlPath is None:
            yamlPath=self.getYamlPath()
        with open(yamlPath, 'r') as stream:
            self.tokens = yaml.safe_load(stream)
        pass
    
    def __init__(self,name:str, lookupName:str=None):
        '''
        construct me for the given name

        Args:
            name(str): name of the Category (type field in the yaml)
            tokenPath(str): path to the yaml file containing the tokens/enum information
        '''
        super().__init__(name,itemFunc=lambda word:self.lookup(word))
        self.lookupByKey={}   
        lookupYamlPath=self.getYamlPath(lookupName) 
        self.read(lookupYamlPath)
        for tokenKey in self.tokens:
            token=self.tokens[tokenKey]
            tokenType=token['type']
            if tokenType==name:
                value=token['value'] if 'value' in token else tokenKey 
                self.lookupByKey[tokenKey]=value
    
    def checkMatch(self,word):
        return self.lookup(word) is not None
    
    def lookup(self,word):
        '''
        lookup the given word
        '''
        if word in self.lookupByKey:
            return self.lookupByKey[word]
        return None
    
    def addLookup(self,key,value):
        '''
        add the given key value pair to my lookup
        '''
        self.lookupByKey[key]=value
    
class OrdinalCategory(EnumCategory):
    '''
    I am the category for ordinals
    '''

    def __init__(self,maxOrdinal=250):
        '''
        Constructor
        '''
        self.maxOrdinal=maxOrdinal
        super().__init__("Ordinal")
        self.prepareLookup()
        
    def prepareLookup(self):
        # https://stackoverflow.com/a/20007730/1497139
        ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
        for i in range(1,self.maxOrdinal):
            # standard decimal ordinal 1., 2., 3. 
            self.addLookup(f"{i}.",i)
            # text ordinal 1st, 2nd, 3rd
            ordinalStr=f"{ordinal(i)}"
            self.addLookup(ordinalStr,i)
            # roman
            self.addLookup(f"{self.toRoman(i)}.",i)
            # using num2words library
            ordinal4i=num2words(i, to='ordinal')
            self.addLookup(ordinal4i,i)
            title=ordinal4i.title()
            self.addLookup(title,i)
            pass       
    
    def toRoman(self,number):
        ''' https://stackoverflow.com/a/11749642/1497139 '''
        if (number < 0) or (number > 3999):
            raise Exception("number needs to be between 1 and 3999")
        if (number < 1): return ""
        if (number >= 1000): return "M" + self.self.toRoman(number - 1000)
        if (number >= 900): return "CM" + self.toRoman(number - 900)
        if (number >= 500): return "D" + self.toRoman(number - 500)
        if (number >= 400): return "CD" + self.toRoman(number - 400)
        if (number >= 100): return "C" + self.toRoman(number - 100)
        if (number >= 90): return "XC" + self.toRoman(number - 90)
        if (number >= 50): return "L" + self.toRoman(number - 50)
        if (number >= 40): return "XL" + self.toRoman(number - 40)
        if (number >= 10): return "X" + self.toRoman(number - 10)
        if (number >= 9): return "IX" + self.toRoman(number - 9)
        if (number >= 5): return "V" + self.toRoman(number - 5)
        if (number >= 4): return "IV" + self.toRoman(number - 4)
        if (number >= 1): return "I" + self.toRoman(number - 1)


class CountryCategory(EnumCategory):
    '''
    I am the category for countries
    '''

    def __init__(self):
        '''
        constructor
        '''
        super().__init__("country", lookupName="countries")
        
class YearCategory(EnumCategory):
    '''
    I am the category for years
    '''

    def __init__(self):
        '''
        constructor
        '''
        super().__init__("year", lookupName="years")