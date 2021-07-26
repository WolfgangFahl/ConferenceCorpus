'''
Created on 26.07.2021

@author: wf
'''
# from lodstorage.entity import EntityManager
# TODO Fix class hierarchy 
from smw.topic import Entity, EntityList

class EventEntity(Entity):
    '''
    base class for Event entities
    '''
    def __init__(self):
        '''
        Constructor
        '''
        pass
      
    def __str__(self):
        '''
        return my
        '''
        text=self.__class__.__name__
        attrs=["pageTitle","acronym","title"]
        delim=":"
        for attr in attrs:
            if hasattr(self, attr):
                value=getattr(self,attr)
                text+=f"{delim}{value}"
                delim=":" 
        return text
        
class EventEntityList(EntityList):
    '''
    Event entity list
    '''
    def __init__(self,listName:str=None,clazz=None,tableName:str=None):
        '''
        constructor 
        '''
        super(EventEntityList, self).__init__(listName,clazz,tableName)