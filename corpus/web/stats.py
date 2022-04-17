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

class Histogrammer:
    '''
    create Histograms
    '''
    def __init__(self,df,bins:int=10):
        '''
        constructor
        '''
        self.df=df
        self.bins=bins
        
    def show(self):
        hist=self.df.hist(bins=self.bins)
        st.pyplot(fig=hist)
        
        

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
st.table(columnFrame)
sql=f"""SELECT COUNT(*) as events, {columnOption} 
FROM {tableOption}
WHERE {columnOption} is not NULL
GROUP BY {columnOption}
ORDER BY 1 DESC"""
st.write(sql)
profiler.time(f"getHistogramm for {columnOption} of {tableOption}")
rows = pd.read_sql(sql,con=sqlDB.c)
profiler.time()
st.table(rows)
hist=Histogrammer(rows)
hist.show()