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
        add an ordinal to the given event record by parsing the title entry
        
        Args:
            record(dict): the event record to add the ordinal information to
            
        '''
        # get the title and ignore record if there is not tile
        title = record.get('title', None)
        if title is None:
            return
        # handle existing ordinal entries - e.g. remove invalid ones
        if "ordinal" in record:
            ordinal = record["ordinal"]
            if ordinal is None:
                del(record["ordinal"])
            elif isinstance(ordinal, str):
                # make sure ordinal is numeric
                if ordinal.isnumeric():
                    record["ordinal"] = int(ordinal)
                else:
                    # ignore non numeric values
                    del record["ordinal"]
        # if there is no ordinal at this point try getting one by parsing the title            
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
        