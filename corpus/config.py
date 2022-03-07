'''
Created on 2021-08-05

@author: wf
'''

class EventDataSourceConfig(object):
    '''
    holds configuration parameters for an EventDataSource
    '''
    def __init__(self,lookupId:str,name:str,title:str,url:str,tableSuffix:str,locationAttribute:str=None):
        '''
        constructor 
        
        Args:
          lookupId(str): the id of the data source
          name(str): the name of the data source
          title(str): the title of the data source
          url(str): the link to the data source homepage
          tableSuffix(str): the tableSuffix to use
          locationAttribute(str): the location Attribute to use
        '''  
        self.lookupId=lookupId
        self.name=name
        self.title=title
        self.url=url
        self.tableSuffix=tableSuffix
        self.locationAttribute=locationAttribute
        
    def getTableName(self,entityName:str):
        '''
        Args:
            entityName(str): the name of the entity
        Return:
            str: the tablename
        '''
        tableName=f"{entityName.lower()}_{self.tableSuffix}"
        return tableName
   
        