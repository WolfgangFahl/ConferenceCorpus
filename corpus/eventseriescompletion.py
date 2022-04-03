'''
Created on 2022-04-03

@author: wf
'''
import re
from num2words import num2words

class EventSeriesCompletion(object):
    '''
    complete a series of events from different datasources 
    '''

    def __init__(self):
        '''
        Constructor
        '''
    
    @classmethod    
    def guessOrdinal(cls,record: dict) -> list:
        """
        tries to guess the ordinal of the given record by returning a set of potential ordinals
        Assumption:
            - given record must have the property 'title'

        Args:
            record: event record

        Returns:
            list of potential ordinals
        """
        title = record.get('title', None)
        if title is None:
            return []
        ord_regex = r"(?P<ordinal>[0-9]+)(?: ?st|nd|rd|th)"
        potentialOrdinal=[]
        match = re.findall(pattern=ord_regex, string=title)
        potentialOrdinal.extend([int(ordinal) for ordinal in match])
        # search for ordinals in textform
        for lang in ['en']:
            for ordinal in range(1,100):
                ordWord = num2words(ordinal, lang=lang, to='ordinal')
                if ordWord in title.lower() or ordWord.replace("-", " ") in title.lower():
                    potentialOrdinal.append(ordinal)
        return list(set(potentialOrdinal))
        