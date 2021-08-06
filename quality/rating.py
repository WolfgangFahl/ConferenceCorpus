'''
Created on 2021-04-16

@author: wf
'''
from enum import Enum
from lodstorage.jsonable import JSONAble

class RatingType(str,Enum):
    '''
    the rating type
    
    see https://stackoverflow.com/a/51976841/1497139 why we use str as a type for better json Encoding
    '''
    missing='❌'
    invalid='👎'
    ok='👍'
    
class Rating(JSONAble):
    '''
    I am rating
    '''

    def __init__(self,pain:int=-1,reason:str=None,hint:str=None):
        '''
        Constructor
        
        Args:
            pain(int): the painLevel
            reason(str): the reason one of missing, invalid or ok
            hint(str): the description of the rating - hint on what is wrong
        '''
        self.set(pain,reason,hint)
        
    @classmethod
    def getSamples(cls):
        samplesLOD=[{
            "pain": 1,
            "reason": RatingType.ok,
            "hint": "Dates,  Jul 13, 2008 , Jul 14, 2008 valid",
        }
        ]
        return samplesLOD
        
    def set(self,pain:int,reason:str,hint:str):
        '''
        set my rating
        '''
        self.pain=pain
        self.reason=reason
        self.hint=hint
        
    def __str__(self):
        return f"{self.pain} - {self.reason}: {self.hint}"