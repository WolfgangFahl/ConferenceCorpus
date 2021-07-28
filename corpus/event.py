'''
Created on 26.07.2021

@author: wf
'''
<<<<<<< HEAD
from lodstorage.entity import EntityManager
from lodstorage.jsonable import JSONAble,JSONAbleList
from lodstorage.storageconfig import StorageConfig
=======
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
>>>>>>> 1099923a0fbab2d36508ab150f8fcfa018aca3aa

class Event(JSONAble):
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
        attrs=["pageTitle","acronym","eventId","title","year","source","url"]
        delim=":"
        for attr in attrs:
            if hasattr(self, attr):
                value=getattr(self,attr)
                text+=f"{delim}{value}"
                delim=":" 
        return text
    
class EventSeries(JSONAble):
    '''
    base class for Event Series entities
    '''
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
class EventSeriesManager(EntityManager):
    '''
    Event series list
    '''
    def __init__(self,name:str,clazz=None,tableName:str=None,primaryKey:str=None,config:StorageConfig=None,debug=False):
        '''
        constructor 
        '''
        super(EventSeriesManager, self).__init__(name=name,entityName="EventSeries",entityPluralName="EventSeries",primaryKey=primaryKey,listName="series",clazz=clazz,tableName=tableName,config=config,debug=debug)
            
class EventManager(EntityManager,JSONAbleList):
    '''
    Event entity list
    '''
<<<<<<< HEAD
    
    def __init__(self,name:str,clazz=None,tableName:str=None,primaryKey:str=None,config:StorageConfig=None,debug=False):
        '''
        constructor 
        '''
        super(EventManager, self).__init__(name=name,entityName="Event",entityPluralName="Events",primaryKey=primaryKey,listName="events",clazz=clazz,tableName=tableName,config=config,debug=debug)
=======
    def __init__(self,**kwargs):
        '''
        constructor 
        '''
        super(EventEntityList, self).__init__()
>>>>>>> 1099923a0fbab2d36508ab150f8fcfa018aca3aa
