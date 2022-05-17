'''
Created on 2022-05-15

@author: wf
'''
import argparse
import numpy
import random
import pprint
import socket
import sys
import traceback

import justpy as jp
from jpwidgets.widgets import LodGrid,MenuButton, MenuLink
from corpus.event import EventStorage
from lodstorage.query import Query,QuerySyntaxHighlight
from lodstorage.lod import LOD


class TabPanel():
    '''
    Tab Panel
    '''
    
    def __init__(self,a,classes='text-white shadow-2 q-mb-md',style="background-color: #1368c8;",align='justify',debug:bool=False):
        '''
        Constructor
        '''
        self.a=a
        self.tabs = jp.QTabs(a=a, classes=classes, style=style , 
                        align=align, narrow_indicator=True, dense=True)
        self.debug=debug
        self.divs={}
        self.tabs.on('input',self.onTabClick)
        
    def setVisibility(self,div,visible:bool):
        '''
        set the visibility of the given div
        '''
        if visible:
            div.style='display:block'
        else:
            div.style='display:none'
            
    def setVisibleTab(self,tabName):
        '''
        set the tab with the given name to visible
        '''
        for divKey,div in self.divs.items():
            self.setVisibility(div,tabName==divKey)
        
    def onTabClick(self, msg):
        '''
        handle clicking of tab
        '''
        if self.debug:
            text=f'tab name={msg.value} was clicked with msg {msg}'
            print(text)
        # change the visible tab
        self.setVisibleTab(msg.value)
        pass
        
    def addTabDiv(self,name,tabLabel):
        '''
        add a tab and create a div to be returned
        
        Args:
            name(str): the name of the tab and prefix for the divs name
            tabLabel(str): the label to be used for the tab
            
        Returns:
            jp.Div: the div created
        '''
        _tab=jp.QTab(name=name,label=tabLabel,a=self.tabs)
        div=jp.Div(a=self.a,name=f"{name}Div")
        self.divs[name]=div
        return div
    
class Queries:
    '''
    pre defined queries
    '''
    def __init__(self):
        self.queries=[{
            "name": "OrdinalHistogramm",
            "query": """SELECT ordinal,count(*) as count
    FROM "%s"
    where ordinal is not null
    group by ordinal
    order by cast(ordinal as int) desc"""
        }]
        self.queriesByName,_dup=LOD.getLookup(self.queries,"name")
        
    def getQuery(self,name,tableName):
        rawQuery=self.queriesByName[name]
        sqlQuery=rawQuery["query"] % tableName
        return sqlQuery

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
        self.queries=Queries()
        self.queryName="OrdinalHistogramm"
        
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
            
    def chart(self,lod):
        self.chartDiv.delete_components()
        # Normal distribution
        data = [numpy.random.normal() for _i in range(1000)]
        chart = jp.Histogram(data, a=self.chartDiv, classes='m-2 border w-1/2')
        chart.options.title.text = 'Normal Distribution Histogram'
        
        
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
    
    def queryHighlight(self,name,sqlQuery):
        query=Query(name=name,query=sqlQuery,lang='sql')
        qs=QuerySyntaxHighlight(query)
        html=qs.highlight()
        return html
        
    def getTotals(self,tableName,columnName=None,withSyntax:bool=False):
        totalSql=f"""SELECT  COUNT(*) as total 
        FROM {tableName}
        """
        if columnName is not None:
            totalSql+=f"WHERE {columnName} is not NULL"
        totalRows=self.sqlDB.query(totalSql)
        total=totalRows[0]["total"]
        html=None
        if withSyntax:
            html=self.queryHighlight(name=f"total for {tableName},{columnName}",sqlQuery=totalSql)
        if columnName is not None:
            result= {"table":tableName,"column":columnName,"count":total}
        else:
            result= {"table":tableName,"total":total}
        return result,html
        
        
    def reloadAgGrid(self,lod:list,showLimit=10):
        self.agGrid.load_lod(lod)
        if self.debug:
            pprint.pprint(lod[:showLimit])
        self.agGrid.options.columnDefs[0].checkboxSelection = True
        
    def onHistogramm(self,_msg):
        try:
            totals=[]
            self.queryDiv.inner_html=""
            for eventView in self.eventViewTables:
                tableName=eventView["name"]
                try:
                    tableTotals,html=self.getTotals(tableName)
                    total=tableTotals["total"]
                    columnTotal,html=self.getTotals(tableName,self.columnName,withSyntax=True)
                    self.queryDiv.inner_html+=html
                    columnTotal["total"]=total
                    columnTotal["percent"]=columnTotal["count"]/total*100
                    totals.append(columnTotal)
                except Exception as totalFail:
                    self.handleException(totalFail) 
            self.reloadAgGrid(totals)
        except Exception as ex:
                self.handleException(ex)
                
    def onQueryClick(self,_msg):
        '''
        handle a click of the query button
        '''
        try:
            sqlQuery=self.queries.getQuery(self.queryName, self.tableName)
            html=self.queryHighlight(self.queryName, sqlQuery)
            self.queryDiv.inner_html=html
            queryLod=self.sqlDB.query(sqlQuery)
            self.reloadAgGrid(queryLod)
            self.chart(queryLod)
        except Exception as ex:
            self.handleException(ex)
                
    def onChangeQuery(self,msg):
        self.queryName=msg.value
            
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
        self.histoGrammButton=MenuButton(a=self.toolbar,text='histogramm',icon="show_chart",click=self.onHistogramm)
        self.queryButton=MenuButton(a=self.toolbar,text='query',icon='question_answer',click=self.onQueryClick)
        
        self.tabDivs={}
        # create tabs
        self.tabPanel = TabPanel(a=self.container)
        self.resultDiv=self.tabPanel.addTabDiv("result", "Results")
        self.chartDiv=self.tabPanel.addTabDiv("chart","Chart")
        self.queryDiv=self.tabPanel.addTabDiv("query","Query")
        self.tabPanel.setVisibleTab("result")
        
        selectorClasses='w-32 m-4 p-2 bg-white'
        self.tableSelect = jp.Select(classes=selectorClasses, a=self.header, value=self.tableName,
            change=self.onChangeTable)
        for tableRecord in self.eventViewTables:
            tableName=tableRecord["name"]
            self.tableSelect.add(jp.Option(value=tableName, text=tableName))
        
        self.columnSelect=jp.Select(classes=selectorClasses, a=self.header, value=self.columnName,
            change=self.onChangeColumn)
        
        self.querySelect=jp.Select(classes=selectorClasses, a=self.header, value=self.queryName,
            change=self.onChangeQuery)
        for queryName in self.queries.queriesByName.keys():
            self.querySelect.add(jp.Option(value=queryName,text=queryName))
        
        self.updateColumnOptions()
        self.agGrid = LodGrid(a=self.resultDiv)
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
    