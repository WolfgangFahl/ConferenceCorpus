'''
Created on 2021-05-31

@author: wf
'''
from collections import Counter
from typing import Tuple, List

from lodstorage.tabulateCounter import TabulateCounter


class Tokenizer(object):
    '''
    categorize some text input
    '''

    def __init__(self, categories):
        self.categories = categories

    def tokenize(self, text, item):
        '''
        tokenize the given text for the given item
        '''
        tokenSequence = TokenSequence(text)
        tokenSequence.match(self.categories, item)
        return tokenSequence


class TokenSequence(object):
    '''
    a sequence of tokens
    '''

    def __init__(self, text: str, separator: str = ' '):
        '''
        constructor
        
        Args:
            separator(str): the separator for the tokens - default: blank
        '''
        self.text = text
        if text:
            self.words = text.split(separator)
        else:
            self.words = []
        self.matchResults: List['Token'] = []

    def next(self) -> Tuple[int, str]:
        """
        get the next token in this sequence

        Returns:
            (int, str): position of the token and the string representation of the token
        """
        for pos, word in enumerate(self.words):
            yield pos, self.words[pos]

    def match(self, categories: list, item: object) -> list:
        '''
        match me for the given categories
        
        Args:
            categories(list): the list of categories to match for
            item(object): the item this token sequence belongs to
        
        '''
        self.item = item
        for pos, tokenStr in self.next():
            for category in categories:
                if category.checkMatch(tokenStr) or (hasattr(category, "checkMatchWithContext")
                                                     and callable(getattr(category, "checkMatchWithContext"))
                                                     and category.checkMatchWithContext(tokenStr, pos, self)):
                    token = Token(category, self, pos, tokenStr, item)
                    self.matchResults.append(token)
        return self.matchResults

    def getTokenOfCategory(self, categoryName: str) -> List['Token']:
        """
        Returns list of matched tokens that are in the given category
        Args:
            categoryName: name of the category the tokens should be in

        Returns:
            list of tokens of the given category
        """
        tokens = [token for token in self.matchResults if token.name == categoryName]
        return tokens

    def __str__(self):
        text=f"{self.text}:{self.matchResults}"
        return text


class Token(object):
    '''
    a single categorized token
    '''

    def __init__(self, category: 'Category', tokenSequence: TokenSequence, pos: int, tokenStr: str, item):
        self.category = category
        self.name = category.name
        self.tokenSequence = tokenSequence
        self.pos = pos
        self.tokenStr = tokenStr
        self.value = category.add(item, tokenStr, pos, tokenSequence)

    def __str__(self):
        text = self.tokenStr
        return text

    def __repr__(self):
        return f"Token({self.__dict__})"


class Category(object):
    '''
    I am a category (a token type) representing an expected part of a signature
    e.g. a date an ordinal, a frequency
    '''

    def __init__(self, name, itemFunc):
        '''
        Constructor
        '''
        self.name = name
        self.items = {}
        self.itemFunc = itemFunc
        self.counter = Counter()
        self.subCategories = {}

    def checkMatch(self, tokenStr: str) -> bool:
        """
        Checks whether the given token lies within the category
        Args:
            tokenStr(str): value of the token

        Returns:
            True if the token is in the category otherwise False
        """
        return NotImplemented

    def checkMatchWithContext(self, tokenStr: str, pos: int, tokenSequence: TokenSequence) -> bool:
        """
        Checks whether the given token lies within the category
        Args:
            tokenStr(str): value of the token
            pos(int): position of the token
            tokenSequence: tokenSequence containing previously matched tokens

        Returns:
            True if the token is in the category otherwise False
        """
        return False

    def addCategory(self, category: 'Category'):
        self.subCategories[category.name] = category

    def add(self, item, propValue, pos:int, tokenSequence: TokenSequence):
        '''
        add the given item with the given value
        '''
        if self.itemFunc is not None:
            value = self.itemFunc(propValue)
        else:
            value = self.getValue(propValue, pos, tokenSequence)
        if value in self.items:
            self.items[value].append(item)
        else:
            self.items[value] = [item]
        self.counter[value] += 1
        return value

    def getValue(self, word: str, pos: int, tokenSequence: TokenSequence):
        """

        Args:
            word: raw token value
            pos: position of the raw token value
            tokenSequence: already matched tokens up to position pos-1

        Returns:
            category value of the token
        """
        return None

    def mostCommonTable(self, tablefmt='pretty', limit=50):
        '''
        get the most common Table
        '''
        tabulateCounter = TabulateCounter(self.counter)
        table = tabulateCounter.mostCommonTable(tablefmt=tablefmt, limit=limit)
        return table
