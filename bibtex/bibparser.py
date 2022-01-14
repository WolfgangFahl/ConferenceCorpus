'''
Created on 2022-01-12

@author: wf
'''
import urllib.request
from pybtex.database.input import bibtex

class BibParser(object):
    '''
    Wraper for BibText parser
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.parser = bibtex.Parser()
        
    def parseUrl(self,url:str):
        '''
        parse the content of a given URL
        
        Args:
            url(str): the URL to get the data to parse from
        '''
        response = urllib.request.urlopen(url)
        bibText = response.read()
        return self.parseText(bibText)
        
    def parseText(self,bibText:str):
        '''
        parse the content of the given bibText
        
        Args:
            bibText(str): the bib text to parse
        '''
        bibData=self.parser.parse_bytes(bibText)
        return bibData
        
        