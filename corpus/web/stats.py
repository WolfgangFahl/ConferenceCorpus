'''
Created on 2022-04-16

@author: wf
'''
from corpus.event import EventStorage
from corpus.utils.download import Profiler
profiler=Profiler("streamlit")
import streamlit as st
profiler.time()
import pandas as pd
import numpy as np
#import plotly.figure_factory as ff
import matplotlib.pyplot as plt
from lodstorage.sql import SQLDB

class Barchart:
    '''
    create Barchart
    '''
    def __init__(self,df,title,x=None,y=None):
        '''
        constructor
        
        Args:
            df(DataFrame): the dataframe to create a barchart for
        '''
        self.df=df
        self.title=title
        columns=self.df.columns.values.tolist()
        if x is None:
            x=columns[0]
        if y is None:
            y=columns[1]
        self.x=x
        self.y=y
        
    def show(self):
        fig, ax = plt.subplots()
        ax.set_ylabel(self.y)
        ax.set_xlabel(self.x)
        ax.set_title(self.title)
        xValues=self.df[self.x].values.tolist()
        yValues=self.df[self.y].values.tolist()
        x = np.arange(len(xValues))
        ax.set_xticks(x, xValues,rotation='vertical')
        
        ax.bar(x,yValues)
        #ax.legend()
        fig.tight_layout()
        st.pyplot(fig=fig)
        
st.title("Histogramm analysis")
sqlDB=EventStorage.getSqlDB()
viewName="event"
viewTables=EventStorage.getViewTableList(viewName)
viewTableFrame=pd.DataFrame(viewTables)
tableOption=st.selectbox("select a source:",viewTableFrame)
#st.write(tableOption)
tableDict=sqlDB.getTableDict()
columns=list(tableDict[tableOption]["columns"])
#st.write(columns)
columnFrame=pd.DataFrame(columns)
columnOption=st.selectbox("select a column:",columnFrame)
totalSql=f"""SELECT  COUNT(*) as total 
FROM {tableOption}
WHERE {columnOption} is not NULL
"""
totalRows=sqlDB.query(totalSql)
total=totalRows[0]["total"]
centileLimit = st.slider('CentileLimit', 0, 20, 10)
#st.table(columnFrame)
havingLimit=round(total*centileLimit/100)
sql=f"""SELECT  {columnOption},COUNT(*) as events 
FROM {tableOption}
WHERE {columnOption} is not NULL
GROUP BY {columnOption}
HAVING COUNT(*)>={havingLimit}
ORDER BY 2 DESC"""
st.write(sql)
title=f"{columnOption} of {tableOption}"
profiler.time(f"getHistogramm for {title}")
rows = pd.read_sql(sql,con=sqlDB.c)
profiler.time()
bc=Barchart(rows,title=title)
bc.show()
st.table(rows)
 