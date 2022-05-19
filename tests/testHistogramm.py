'''
Created on 17.05.2022

@author: wf
'''
from statistics import mean
from typing import List

from tabulate import tabulate

from corpus.utils.plots import Histogramm, PlotSettings, Zipf
from tests.basetest import BaseTest
from corpus.event import EventStorage
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pdffit.distfit import BestFitDistribution

from collections import Counter
import re
import os
import sys

class DataSource():
    '''
    helper class for datasource information
    '''
    def __init__(self,tableRecord):
        '''
        '''
        self.table=tableRecord
        self.tableName=tableRecord["name"]
        self.name=self.tableName.replace("event_","")
        self.title=self.name
        
        if self.title.startswith("or"):
            self.title="OpenResearch"
        if self.title=="ceurws": self.title="CEUR-WS"
        if self.title=="gnd": self.title="GND"
        if self.title=="tibkat": self.title="TIBKAT"
        if self.title=="crossref": self.title="Crossref"
        if self.title=="wikicfp": self.title="WikiCFP"
        if self.title=="wikidata": self.title="Wikidata"
        seriesColumnLookup = {
            "orclone": "inEventSeries",
            "dblp": "series",
            #("confref", "seriesId"),
            "wikicfp": "seriesId",
            "wikidata": "eventInSeriesId"
        }
        self.seriescolumn=seriesColumnLookup.get(self.name,None)
        pass
    
    def __str__(self):
        text=f"{self.title}:{self.name}:{self.tableName}"
        return text
    
    @classmethod
    def getAll(cls):
        cls.sources={}
        for source in cls.getDatasources():
            cls.sources[source.name]=source

    @classmethod
    def getDatasources(cls):
        '''
        get the datasources
        '''
        eventViewTables=EventStorage.getViewTableList("event")
        sources=[DataSource(tableRecord)  for tableRecord in eventViewTables]
        sortedSources=sorted(sources, key=lambda ds: ds.name)
        return sortedSources

class TestHistogramm(BaseTest):
    '''
    test the histogramm class with example data
    '''
    
    def setUp(self, debug=False, profile=True):
        BaseTest.setUp(self, debug=debug, profile=profile)
        self.histroot="/tmp/histogramms"
        os.makedirs(self.histroot,exist_ok=True)
        DataSource.getAll()
        
    def wikiFigure(self,dataSource,sqlQuery,fileName,fileTitle="histogramm",px=600):
        '''
        create mediawiki markup to show the given outputFilename and sqlQuery
        '''
        markup=f"""== {dataSource.title} =="""
        if sqlQuery:
            markup+=f"""
=== sql query ===
<source lang='sql'>
{sqlQuery}
</source>"""
        markup+=f"""
=== {fileTitle} ===
[[File:{fileName}|{px}px]]
        """
        return markup 
        
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
        return lod
    
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
        
        for dataSource in DataSource.sources.values():
            # loop over all datasources
            histOutputFileName=f"ordinalhistogramm_{dataSource.tableName}.png"
            zipfOutputFileName=f"zipf_{dataSource.tableName}.png"
            print(f"""== {dataSource.title}==
[[File:{histOutputFileName}|600px]]  
[[File:{zipfOutputFileName}|600px]]        
            """)    
            try:
                maxValue=75 if dataSource in  ["tibkat","gnd"] else 50
                lod=self.getLod(dataSource.tableName,maxValue=maxValue)
                values=[record["ordinal"] for record in lod]
                h=Histogramm(x=values)
                hps=PlotSettings(outputFile=f"{self.histroot}/{histOutputFileName}",callback=histogrammSettings)
                h.show(xLabel='ordinal',yLabel='count',title=f'{dataSource.title} Ordinals',alpha=0.6,ps=hps)
                
                # zipf distribution without first value
                z=Zipf(values,minIndex=1)
                zps=PlotSettings(outputFile=f"{self.histroot}/{zipfOutputFileName}")
                z.show(f'{dataSource.title} Zipf',ps=zps)
            except Exception as ex:
                print(ex,file=sys.stderr)
                pass


    def latexFigure(self,caption,figLabel,fileName,scale=0.5):
        '''
        get the latex Code for the given figure
        '''
        latex="""\\begin{figure}
    \centering
    {\includegraphics[scale=%s]{%s}}
    \caption{%s}
    \label{fig:%s}
\end{figure}"""
        return latex % (scale,fileName,caption,figLabel)

    def testSeriesCompletenessHistogramm(self):
        '''
        test the event series completeness
        '''
        def histogrammSettings(plot):
            '''
            optional call back to add more data to histogramm
            '''
            pass

        for datasource in DataSource.sources.values():
            if datasource.seriescolumn:
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
                    """ % (datasource.seriescolumn, datasource, datasource.seriescolumn)
                sqlDB = EventStorage.getSqlDB()
                lod = sqlDB.query(sqlQuery)
                values = [round(record["completeness"],2) for record in lod if isinstance(record["completeness"], float)]
                values.sort()
                print(datasource,len(values),"→", len(values) // 2)
                threshold = values[len(values) // 2]
                h = Histogramm(x=values)
                histOutputFileName=f"{datasource}_series_completeness.png"
                latex=self.latexFigure(scale=0.5, caption=f"event series completeness of {datasource}", figLabel=f"esc-{datasource}", fileName=histOutputFileName)
                print(self.wikiFigure(datasource,sqlQuery,histOutputFileName))
                print(latex)
                hps = PlotSettings(outputFile=f"{self.histroot}/{histOutputFileName}", callback=histogrammSettings)
                # density not working?
                # https://stackoverflow.com/questions/55555466/matplotlib-hist-function-argument-density-not-working
                h.show(xLabel='completeness',
                       yLabel='distribution',
                       title=f'{datasource}_series_completeness',
                       density=True,
                       alpha=0.8,
                       ps=hps,
                       bins=10,
                       vlineAt=threshold)

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
        for dataSource in DataSource.sources.values():
            if dataSource.name in ["acm"]:
                continue
            print(dataSource)
            histOutputFileName=f"eventSeriesCompletionByAcronymHistogramm_{dataSource.tableName}.png"
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
            values = [round(record["completeness"], 2) for record in aggLod if isinstance(record["completeness"], float)]
            values.sort()
            threshold =values[len(values)//2]
            h = Histogramm(x=values)
            hps = PlotSettings(outputFile=f"{self.histroot}/{histOutputFileName}", callback=histogrammSettings)
            h.show(xLabel='completeness',
                   yLabel='distribution',
                   title=f'{dataSource.title} Series completeness',
                   alpha=0.7,
                   density=True,
                   ps=hps,
                   bins=10,
                   vlineAt=threshold)
            latex = self.latexFigure(scale=0.5, caption=f"event series completeness of {dataSource.title}",
                                     figLabel=f"esca-{dataSource.name}", fileName=histOutputFileName)
            
            print(self.wikiFigure(dataSource, sqlQuery=None, fileName=histOutputFileName))
            print(latex)
            
            print(dataSource, len(values), "→", len(values) // 2)
            if debug:
                aggLod.sort(key=lambda r:r.get("completeness"), reverse=True)
                print(len(aggLod))
                print(tabulate(aggLod, tablefmt="mediawiki", headers="keys"))