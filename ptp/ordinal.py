'''
Created on 2022-04-05

@author: wf
'''
from ptp.parsing import Tokenizer
from ptp.signature import OrdinalCategory

class Ordinal(object):
    '''
    Ordinal
    '''
    tokenizer=None

    @classmethod   
    def addParsedOrdinal(cls,record:dict):
        '''
        add a 
        '''
        if "ordinal" in record:
            ordinal = record["ordinal"]
            if ordinal is None:
                del(record["ordinal"])
            elif isinstance(ordinal, str):
                if ordinal.isnumeric():
                    record["ordinal"] = int(ordinal)
                else:
                    del record["ordinal"]
        title = record.get('title', None)
        if title is None:
            return
        if not "ordinal" in record:
            # we always use "ordinal-parsing" as the item since we are not interested in stats
            item="ordinal-parsing"
            pol=cls.parseOrdinals(title,item) 
            if len(pol)==1:
                record["ordinal"]=pol[0]
     
    @classmethod    
    def parseOrdinals(cls,title:str,item:object) -> list:
        """
        parses the given title returning a set of potential ordinals
        
        Args:
            title: the title to parse

        Returns:
            list ordinals found
        """
        if cls.tokenizer is None:
            cls.tokenizer=Tokenizer([OrdinalCategory()])
        tokenSequence=cls.tokenizer.tokenize(title, item)
        ordinals=[]
        for token in tokenSequence.matchResults:
            ordinals.append(token.value)
            pass
        return ordinals
        