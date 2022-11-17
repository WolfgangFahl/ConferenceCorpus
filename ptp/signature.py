'''
Created on 2021-05-03

Proceedings Title signature elements
@author: wf
'''
from functools import reduce
from typing import Union

from ptp.parsing import Category
from num2words import num2words
import re
import yaml
import pathlib
from pyparsing import ParseException
import pyparsing as pp


class RegexpCategory(Category):
    '''
    category defined by a regular expression
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
   
    def getYamlPath(self,lookupName:str):
        '''
        get the YamlPath for the given filename prefix
        
        Args:
            filename(str): the prefix of the filename to get the Yaml path for
            
        Returns:
            str: the string representation of the path
        '''
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
        if lookupName is None:
            multiType=True
            lookupName="dictionary"
        else:
            multiType=False
        lookupYamlPath=self.getYamlPath(lookupName) 
        self.read(lookupYamlPath)
        # loop over all tokens
        for tokenKey in self.tokens:
            token=self.tokens[tokenKey]
            # get the token
            if multiType:
                tokenType=token['type']
                valid=tokenType==name
            else:
                valid=True
            if valid:
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

    @classmethod
    def toRoman(cls,number):
        ''' https://stackoverflow.com/a/11749642/1497139 '''
        if (number < 0) or (number > 3999):
            raise Exception("number needs to be between 1 and 3999")
        if (number < 1): return ""
        if (number >= 1000): return "M" + cls.toRoman(number - 1000)
        if (number >= 900): return "CM" + cls.toRoman(number - 900)
        if (number >= 500): return "D" + cls.toRoman(number - 500)
        if (number >= 400): return "CD" + cls.toRoman(number - 400)
        if (number >= 100): return "C" + cls.toRoman(number - 100)
        if (number >= 90): return "XC" + cls.toRoman(number - 90)
        if (number >= 50): return "L" + cls.toRoman(number - 50)
        if (number >= 40): return "XL" + cls.toRoman(number - 40)
        if (number >= 10): return "X" + cls.toRoman(number - 10)
        if (number >= 9): return "IX" + cls.toRoman(number - 9)
        if (number >= 5): return "V" + cls.toRoman(number - 5)
        if (number >= 4): return "IV" + cls.toRoman(number - 4)
        if (number >= 1): return "I" + cls.toRoman(number - 1)


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


class RomanNumeral(pp.OneOrMore):
    """
    matches roman numerals
    see https://github.com/pyparsing/pyparsing/blob/master/jpexamples/romanNumerals.py
    limited to number up to 99
    """

    def __init__(self, limit:int=None, name:str=None):
        """
        constructor
        """
        if name is None:
            name = "roman"
        map = [("I", 1), ("IV", 4), ("V", 5), ("IX", 9), ("X", 10), ("XL", 40), ("L", 50), ("XC", 90), ("C", 100),
               ("CD", 400), ("D", 500), ("CM", 900), ("M", 1000)]
        expressions = [self.romanNumeralLiteral(numeralString, value) for numeralString, value in map if limit is None or value < limit]
        numeral = reduce(lambda a, b: b|a, expressions).leaveWhitespace()
        super(RomanNumeral, self).__init__(numeral[1, ...])
        self.setParseAction(sum)
        self.setName(name)

    @classmethod
    def romanNumeralLiteral(cls, numeralString, value):
        return pp.Literal(numeralString).setParseAction(pp.replaceWith(value))


class VolumeCategory(Category):
    """
    I am a category for volumes
    """
    VOLUME_LABEL = pp.Group(pp.CaselessLiteral("volume") |
                            pp.CaselessLiteral("vol.") |
                            pp.CaselessLiteral("vol") |
                            pp.CaselessLiteral("part") |
                            pp.CaselessLiteral("pt.")
                            )("label")
    VOLUME_VALUE_NUMERIC = pp.Word(pp.nums).setParseAction(pp.pyparsing_common.convertToInteger).setName("numeric")
    VOLUME_VALUE_ALPHA = pp.Char(pp.alphas).setParseAction(pp.tokenMap(lambda value: ord(value.lower())-96)).setName("alphanumeric")
    VOLUME_VALUE = pp.Group(VOLUME_VALUE_NUMERIC | RomanNumeral(limit=100, name="roman reduced") | VOLUME_VALUE_ALPHA)("value")
    VOLUME = VOLUME_LABEL + pp.Optional(" ") + VOLUME_VALUE

    def __init__(self):
        """
        constructor
        """
        super().__init__("volume", self.getValue)

    def checkMatch(self, word:str) -> bool:
        return self.VOLUME.matches(word)

    def checkMatchWithContext(self, tokenStr: str, pos: int, tokenSequence) -> bool:
        matches = False
        if self.VOLUME_LABEL.matches(tokenStr):
            matches = True
        else:
            previousTokens = tokenSequence.getTokenOfCategory(self.name)
            tokensAtPreviousPosition = [token for token in previousTokens if token.pos == pos-1]
            if len(tokensAtPreviousPosition) == 1:
                tokenAtPreviousPosition = tokensAtPreviousPosition[0]
                if tokenAtPreviousPosition.value == "LABEL":
                    # previous token is volume label → match against volume value
                    matches = self.VOLUME_VALUE.matches(tokenStr)
        return matches


    def getValue(self, word:str) -> Union[str, int, None]:
        """
        returns the value of the given word.
        LABEL if the word is the volume label
        <integer> if the word is the volume label
        Args:
            word: word to parse the value for

        Returns:
            value of the given word
        """
        res = None
        if self.VOLUME.matches(word):
            parsedValue = self.VOLUME.parseString(word).asDict()
            vals = [m for m,_,_ in self.VOLUME.scanString(word)]
            res = parsedValue.get("value")[0]
        elif self.VOLUME_LABEL.matches(word):
            res = "LABEL"
        elif self.VOLUME_VALUE.matches(word):
            res = int(self.VOLUME_VALUE.parseString(word)["value"][0])
        return res


class CityPrefixCategory(EnumCategory):
    '''
    I am the category for countries
    '''

    def __init__(self):
        '''
        constructor
        '''
        super().__init__("cityPrefix", lookupName="cityNamePrefixes")


class CityCategory(EnumCategory):
    '''
    I am the category for countries
    '''

    def __init__(self):
        '''
        constructor
        '''
        super().__init__("city", lookupName="cityNames")
        self.itemFunc=None

    def checkMatchWithContext(self, tokenStr: str, pos: int, tokenSequence) -> bool:
        fullname = self.getTokenStrWithPrefixes(tokenStr, pos, tokenSequence)
        matches = self.checkMatch(fullname)
        return matches

    def getValue(self, word: str, pos: int, tokenSequence):
        fullname = self.getTokenStrWithPrefixes(word, pos, tokenSequence)
        value = self.lookup(fullname)
        return value

    def getTokenStrWithPrefixes(self, tokenStr: str, pos:int, tokenSequence) -> str:
        tokenStr = tokenStr.strip(",;")
        cityPrefixTokens = [token for token in tokenSequence.matchResults if
                            isinstance(token.category, CityPrefixCategory)]
        cityPrefixTokens = [token for token in cityPrefixTokens if pos in [token.pos + prefixPos for prefixPos in
                                                                           [int(pos) for pos in
                                                                            token.value.split(",")]]]
        cityPrefixTokens.sort(key=lambda token: token.pos)
        fullname = " ".join([token.tokenStr for token in cityPrefixTokens]) + " " + tokenStr
        return fullname.strip()

class AcronymCategory(EnumCategory):
    '''
    I am the category for acronyms
    '''

    def __init__(self):
        '''
        constructor
        '''
        super().__init__("acronym", lookupName="acronyms")

    @staticmethod
    def sanitize(word:str):
        if isinstance(word, str):
            return word.strip(" ()#")

    def checkMatch(self, word):
        return super().checkMatch(self.sanitize(word))

    def lookup(self, word):
        return super().lookup(self.sanitize(word))