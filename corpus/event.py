'''
Created on 26.07.2021

@author: wf
'''
# from lodstorage.entity import EntityManager
# TODO Fix class hierarchy
from lodstorage.jsonable import JSONAbleList, JSONAble


class EntityList(object):
    '''
    ToDo: Migrate to pyLODstorage?
    '''

    def __init__(self):
        pass


class Entity(object):
    '''
    ToDo: Migrate to pyLODstorage?
    '''

    def __init__(self):
        pass

class EventEntity(Entity):
    '''
    base class for Event entities
    '''
    def __init__(self,**kwargs):
        '''
        Constructor
        '''
        super().__init__()

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
    def __init__(self,**kwargs):
        '''
        constructor 
        '''
        super(EventEntityList, self).__init__()