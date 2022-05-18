'''
Created on 17.05.2022

@author: wf
'''
from corpus.utils.plots import Histogramm, PlotSettings, Zipf
from tests.basetest import BaseTest
from corpus.event import EventStorage
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pdffit.distfit import BestFitDistribution
import os
import sys


class TestHistogramm(BaseTest):
    '''
    test the histogramm class
    '''
    
    def setUp(self, debug=False, profile=True):
        BaseTest.setUp(self, debug=debug, profile=profile)
        self.histroot="/tmp/histogramms"
        os.makedirs(self.histroot,exist_ok=True)
    
    def getLod(self,tableName="event_ceurws",maxValue=75):
        sqlQuery="""SELECT ordinal
    FROM %s
    where ordinal is not null
    and ordinal < %s
    """ % (tableName,maxValue)
    
        sqlDB=EventStorage.getSqlDB()
        lod=sqlDB.query(sqlQuery)
        return lod
    
    def getDatasources(self):
        eventViewTables=EventStorage.getViewTableList("event")
        names=[tableRecord["name"].replace("event_","")  for tableRecord in eventViewTables]
        return names
    
    def eventSeriesCompleteness(self):
        for tableName in self.getDatasources():
            print(tableName)
            
    def testZipf(self):
        '''
        test the Zipf distribution
        '''
        show=False
        for a in [1.2,1.4,1.6]:
            x = np.random.zipf(a=a, size=1000)
            xlog=np.log(x)
            df = pd.Series(xlog) 
            # distributionNames=["powerlaw","norm"]
            
            bfd=BestFitDistribution(df)
            bfd.analyze(f"Zipf distribution a={a:.1f}", x_label="x", y_label="zipf(x,a)",density=False,outputFilePrefix=f"/tmp/zipf{a}")
        if show:
            plt.show()
        
    
    def testHistogramms(self):
        '''
        test histogramm
        '''
        def histogrammSettings(plot):
            #plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
            plot.plt.xlim(1, maxValue)
            #plt.ylim(0, 0.03)
            pass
        
        for dataSource in self.getDatasources():
            tableName=f"event_{dataSource}"
            histOutputFileName=f"ordinalhistogramm_{tableName}.png"
            zipfOutputFileName=f"zipf_{tableName}.png"
            print(f"""== {dataSource}==
[[File:{histOutputFileName}|600px]]  
[[File:{zipfOutputFileName}|600px]]        
            """)    
            try:
                maxValue=75 if dataSource in  ["tibkat","gnd"] else 50
                lod=self.getLod(tableName,maxValue=maxValue)
                values=[record["ordinal"] for record in lod]
                h=Histogramm(x=values)
                hps=PlotSettings(outputFile=f"{self.histroot}/{histOutputFileName}",callback=histogrammSettings)
                h.show(xLabel='ordinal',yLabel='count',title=f'{dataSource} Ordinals',alpha=0.6,ps=hps)
                z=Zipf(values=values)
                zps=PlotSettings(outputFile=f"{self.histroot}/{zipfOutputFileName}")
                z.show(f'{dataSource} Zipf',ps=zps)
            except Exception as ex:
                print(ex,file=sys.stderr)
                pass


    def testSeriesCompletenessHistogramm(self):
        def histogrammSettings(plot):
            #plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
            #plot.plt.xlim(1, maxValue)
            #plt.ylim(0, 0.03)
            pass

        datasources = [
            ("orclonebackup", "inEventSeries"),
            ("dblp", "series"),
            ("confref", "seriesId"),
            ("wikicfp", "seriesId")
        ]
        for datasource, seriesCol in datasources:
            sqlQuery = """SELECT 
                               %s,
                               min(ordinal) as minOrdinal, 
                               max(ordinal) as maxOrdinal,
                               avg(ordinal) as avgOrdinal,
                               max(Ordinal)-min(Ordinal) as available,
                               (max(Ordinal)-min(Ordinal)) /(max(Ordinal)-1.0) as completeness
                            FROM event_%s
                            Where ordinal is not null 
                            group by %s
                            order by 6 desc
                """ % (seriesCol, datasource, seriesCol)

            sqlDB = EventStorage.getSqlDB()
            lod = sqlDB.query(sqlQuery)
            values = [round(record["completeness"],2) for record in lod if isinstance(record["completeness"], float)]
            h = Histogramm(x=values)
            histOutputFileName=f"{datasource}_series_completeness.png"
            hps = PlotSettings(outputFile=f"{self.histroot}/{histOutputFileName}", callback=histogrammSettings)
            h.show(xLabel='completeness',
                   yLabel='count',
                   title=f'{datasource}_series_completeness',
                   alpha=0.8,
                   ps=hps,
                   bins=20)