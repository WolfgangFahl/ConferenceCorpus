'''
Created on 2022-05-15

@author: wf
'''
import argparse
import pprint
import socket
import traceback
import justpy as jp
from jpwidgets.widgets import LodGrid,MenuButton, MenuLink, QAlert,QPasswordDialog
from corpus.event import EventStorage
import sys

class Dashboard():
    '''
    statistics dashboard for the conference corpus
    '''
    def __init__(self,debug:bool=False):
        self.debug=debug
        self.sqlDB=EventStorage.getSqlDB()
        self.eventViewTables=EventStorage.getViewTableList("event")
        self.setTableName(self.eventViewTables[0]["name"])
        self.columnName="source"
        
    def handleException(self,ex):
        '''
        handle the given exception
        
        Args:
            ex(Exception): the exception to handle
        '''
        errorMsg=str(ex)
        trace=""
        if self.debug:
            trace=traceback.format_exc()
        errorMsgHtml=f"{errorMsg}<pre>{trace}</pre>"
        self.errors.inner_html=errorMsgHtml
        print(errorMsg)
        if self.debug:
            print(trace)
 
    def qtab_click(self, msg):
        """function runs when user clicks a QTab"""
        # do something here
        print(f'tab name={self.value} was clicked')
        
    def onChangeTable(self, msg:dict):
        '''
        handle selection of a different table
        
        Args:
            msg(dict): the justpy message
        '''
       
        if self.debug:
            print(msg)
        self.setTableName(msg.value)
        self.updateColumnOptions()
        
    def onChangeColumn(self,msg:dict):
        '''
        handle change of column selection
        
        '''
        self.columnName=msg.value
        pass
        
    def getTotals(self,tableName,columnName=None):
        totalSql=f"""SELECT  COUNT(*) as total 
        FROM {tableName}
        """
        if columnName is not None:
            totalSql+=f"WHERE {columnName} is not NULL"
        totalRows=self.sqlDB.query(totalSql)
        total=totalRows[0]["total"]
        if columnName is not None:
            return {"table":tableName,"column":columnName,"count":total}
        else:
            return {"table":tableName,"total":total}
        
    def reloadAgGrid(self,lod:list,showLimit=10):
        self.agGrid.load_lod(lod)
        if self.debug:
            pprint.pprint(lod[:showLimit])
        self.agGrid.options.columnDefs[0].checkboxSelection = True
        
    def onHistogramm(self,_msg):
        try:
            totals=[]
            for eventView in self.eventViewTables:
                tableName=eventView["name"]
                try:
                    total=self.getTotals(tableName)["total"]
                    columnTotal=self.getTotals(tableName,self.columnName)
                    columnTotal["total"]=total
                    columnTotal["percent"]=columnTotal["count"]/total*100
                    totals.append(columnTotal)
                except Exception as totalFail:
                    self.handleException(totalFail) 
            self.reloadAgGrid(totals)
        except Exception as ex:
                self.handleException(ex)
            
    def setTableName(self,tableName:str):
        '''
        
        Args:
            tableName(str): the table name
        '''
        self.tableName=tableName
        tableDict=self.sqlDB.getTableDict()
        self.columns=list(tableDict[tableName]["columns"])
        
    def updateColumnOptions(self):
        self.columnSelect.delete_components()
        for columnName in self.columns:
            self.columnSelect.add(jp.Option(value=columnName, text=columnName))
   

    def webPage(self):
        '''
        Returns:
            a Justpy reactive webPage
        '''
        self.wp = jp.QuasarPage()
        self.container=jp.Div(a=self.wp)
        self.errors=jp.Span(a=self.container,style='color:red')
        self.header=jp.Div(a=self.container)
        self.toolbar=jp.QToolbar(a=self.header)
        MenuLink(a=self.toolbar,text='github',icon='forum', href="https://github.com/WolfgangFahl/ConferenceCorpus")
        self.histoGrammButton=MenuButton(a=self.toolbar,text='histogramm',icon="calc",click=self.onHistogramm)
  
        # create tabs
        tabs = jp.QTabs(a=self.container, classes='text-white shadow-2 q-mb-md', style="background-color: #00305e;", 
                        align='justify', narrow_indicator=True, dense=True)
        tab1 = jp.QTab(a=tabs, name='tab_1', label='Tab 1')
        tab2 = jp.QTab(a=tabs, name='tab_2', label='Tab 2')
        tab3 = jp.QTab(a=tabs, name='tab_3', label='Tab 3')
        tabs.on('input', self.qtab_click)
        selectorClasses='w-32 m-4 p-2 bg-white'
        self.tableSelect = jp.Select(classes=selectorClasses, a=self.header, value=self.tableName,
            change=self.onChangeTable)
        for tableRecord in self.eventViewTables:
            tableName=tableRecord["name"]
            self.tableSelect.add(jp.Option(value=tableName, text=tableName))
        self.columnSelect=jp.Select(classes=selectorClasses, a=self.header, value=self.columnName,
            change=self.onChangeColumn)
        self.updateColumnOptions()
        self.agGrid = LodGrid(a=self.container)
        return self.wp

def main(_argv=None):
    '''
    command line entry point
    '''
    parser = argparse.ArgumentParser(description='blackjack demo')
    parser.add_argument('--host',default=socket.getfqdn())
    parser.add_argument('--port',type=int,default=8000)
    args = parser.parse_args()
    dashboard=Dashboard()
    jp.justpy(dashboard.webPage,host=args.host,port=args.port)

if __name__ == '__main__':
    sys.exit(main())    
    