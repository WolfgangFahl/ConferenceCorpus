'''
Created on 17.05.2022

@author: wf
'''
from statistics import mean
from typing import List

from tabulate import tabulate
from corpus.eventcorpus import DataSource
from corpus.utils.plots import Histogramm, PlotSettings, Zipf
from tests.basetest import BaseTest
from corpus.event import EventStorage
from corpus.utils.figure import Figure,FigureList

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pdffit.distfit import BestFitDistribution

from collections import Counter
import re
import os
import sys

class TestHistogramm(BaseTest):
    '''
    test the histogramm class with example data
    '''
    
    def setUp(self, debug=False, profile=True):
        BaseTest.setUp(self, debug=debug, profile=profile)
        self.histroot="/tmp/histogramms"
        os.makedirs(self.histroot,exist_ok=True)
        DataSource.getAll()
        self.alpha=0.7
        
    def testSources(self):
        '''
        check the source handling
        '''
        self.assertTrue(len(DataSource.sources)>=9)
        for source in DataSource.sources.values():
            if self.debug:
                print(source)
    
    def getLod(self,tableName="event_ceurws",maxValue=75):
        sqlQuery="""SELECT ordinal
    FROM %s
    where ordinal is not null
    and ordinal < %s
    """ % (tableName,maxValue)
    
        sqlDB=EventStorage.getSqlDB()
        lod=sqlDB.query(sqlQuery)
        return sqlQuery,lod
    
    def testZipfPlot(self):
        '''
        test the zipf plot
        '''
        counter=Counter()
        counter[1]=8
        counter[2]=4
        counter[3]=2
        zipf=Zipf(counter,minIndex=1)
        self.assertEqual(3.0,zipf.mean)
        pass
        
        
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
    
    def testOrdinalHistogramms(self):
        '''
        test histogramm
        '''
        def histogrammSettings(plot):
            #plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
            plot.plt.xlim(1, maxValue)
            #plt.ylim(0, 0.03)
            pass
        self.figureList=FigureList(caption="ordinal Histogramms",figureListLabel="ordHist")
        for dataSource in DataSource.sources.values():
            # loop over all datasources
            histOutputFileName=f"ordinalHistogramm-{dataSource.name}.png"
            zipfOutputFileName=f"ordinalHistogrammZipf-{dataSource.name}.png"
            try:
                print(f"creating histogramm for {dataSource}")
                maxValue=75 if dataSource in  ["tibkat","gnd"] else 50
                sqlQuery,lod=self.getLod(dataSource.tableName,maxValue=maxValue)
                figure=Figure(dataSource.title,caption=f"{dataSource.name} ordinals",figLabel=f"ord-{dataSource.name}",sqlQuery=sqlQuery,fileNames=[histOutputFileName,zipfOutputFileName])
                if dataSource.name!="confref":
                    self.figureList.add(figure)
                values=[record["ordinal"] for record in lod]
                h=Histogramm(x=values)
                hps=PlotSettings(outputFile=f"{self.histroot}/{histOutputFileName}",callback=histogrammSettings)
                h.show(xLabel='ordinal',yLabel='count',title=f'{dataSource.title} Ordinals',alpha=self.alpha,ps=hps)
                
                # zipf distribution without first value
                z=Zipf(values,minIndex=1)
                zps=PlotSettings(outputFile=f"{self.histroot}/{zipfOutputFileName}")
                z.show(f'{dataSource.title} Zipf',ps=zps)
            except Exception as ex:
                print(ex,file=sys.stderr)
                pass
        self.figureList.printAllMarkups()
    

    def testSeriesCompletenessHistogramm(self):
        '''
        test the event series completeness
        '''
        def histogrammSettings(plot):
            '''
            optional call back to add more data to histogramm
            '''
            pass
        self.figureList=FigureList(caption="event Series completeness",figureListLabel="eventcomp",cols=2)
        for dataSource in DataSource.sources.values():
            if dataSource.seriescolumn:
                sqlQuery = """SELECT 
       %s,
       min(ordinal) as minOrdinal, 
       max(ordinal) as maxOrdinal,
       avg(ordinal) as avgOrdinal,
       max(Ordinal)-min(Ordinal) as ordinalRange,
       (max(Ordinal)-min(Ordinal)) /(max(Ordinal)-1.0) as completeness
FROM %s
WHERE ordinal is not null 
GROUP BY %s
ORDER by 6 DESC
                    """ % (dataSource.seriescolumn, dataSource.tableName, dataSource.seriescolumn)
                sqlDB = EventStorage.getSqlDB()
                lod = sqlDB.query(sqlQuery)
                values = [round(record["completeness"],2) for record in lod if isinstance(record["completeness"], float)]
                values.sort()
                print(dataSource,len(values),"→", len(values) // 2)
                threshold = values[len(values) // 2]
                h = Histogramm(x=values)
                histOutputFileName=f"eventSeriesCompleteness-{dataSource.name}.png"
                figure=Figure(dataSource.title,caption=f"event series completeness of {dataSource.name}",figLabel=f"esc-{dataSource.name}",sqlQuery=sqlQuery,fileNames=[histOutputFileName])
                self.figureList.add(figure)
                hps = PlotSettings(outputFile=f"{self.histroot}/{histOutputFileName}", callback=histogrammSettings)
                # density not working?
                # https://stackoverflow.com/questions/55555466/matplotlib-hist-function-argument-density-not-working
                h.show(xLabel='completeness',
                       yLabel='distribution',
                       title=f'{figure.title}',
                       density=True,
                       alpha=self.alpha,
                       ps=hps,
                       bins=10,
                       vlineAt=threshold)
        self.figureList.printAllMarkups()

    def testSeriesCompletenessHistogrammByAcronym(self):
        '''
        acronym based histogramms
        '''
        def histogrammSettings(plot):
            '''
            optional callback to add more data to histogramm
            '''
            pass
        
        debug = False
        self.figureList=FigureList(caption="event Series completeness by acronym",figureListLabel="eventcompa",cols=3)
        for dataSource in DataSource.sources.values():
            if dataSource.name in ["acm"]:
                continue
            print(dataSource)
            histOutputFileName=f"eventSeriesCompletionByAcronymHistogramm_{dataSource.name}.png"
            sqlQuery = """SELECT acronym, ordinal
                FROM %s
                """ % (dataSource.tableName)
            sqlDB = EventStorage.getSqlDB()
            lod = sqlDB.query(sqlQuery)
            series = {}
            acronymRegexp = r'(?P<acronym>[A-Z]+)\s*[0-9]+'
            for d in lod:
                acronym = d.get('acronym')
                if acronym:
                    match = re.fullmatch(acronymRegexp, acronym)
                    if match is None:
                        continue
                    seriesAcronym = match.group("acronym")
                    if isinstance(seriesAcronym, str):
                        if seriesAcronym in series:
                            series[seriesAcronym].append(d)
                        else:
                            series[seriesAcronym] = [d]
            aggLod = []
            for series, eventRecords in series.items():
                ordinals: List[int] = [int(r.get("ordinal"))
                                       for r in eventRecords
                                       if r.get("ordinal")
                                       and (isinstance(r.get("ordinal"), str) and r.get("ordinal").isnumeric()) or isinstance(r.get("ordinal"), int)]
                if len(ordinals) == 0:
                    continue
                minOrd = min(ordinals)
                maxOrd = max(ordinals)
                res = {
                    "series": series,
                    "minOrdinal": minOrd,
                    "maxOrdinal": maxOrd,
                    "avgOrdinal": mean(ordinals),
                    "available": maxOrd - minOrd,
                    "completeness": (maxOrd-minOrd) / (maxOrd-1) if maxOrd>1 else 1
                }
                aggLod.append(res)
            figure=Figure(dataSource.title,caption=f"event series completeness of {dataSource.name}",figLabel=f"esca-{dataSource.name}",sqlQuery=None,fileNames=[histOutputFileName])
            self.figureList.add(figure)
              
            values = [round(record["completeness"], 2) for record in aggLod if isinstance(record["completeness"], float)]
            values.sort()
            threshold =values[len(values)//2]
            h = Histogramm(x=values)
            hps = PlotSettings(outputFile=f"{self.histroot}/{histOutputFileName}", callback=histogrammSettings)
            h.show(xLabel='completeness',
                   yLabel='distribution',
                   title=f'{figure.title}',
                   alpha=self.alpha,
                   density=True,
                   ps=hps,
                   bins=10,
                   vlineAt=threshold)
        
            print(dataSource, len(values), "→", len(values) // 2)
        self.figureList.printAllMarkups()