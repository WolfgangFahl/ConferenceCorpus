'''
Created on 17.05.2022

@author: wf
'''
import datetime
from statistics import mean
from typing import List

from dateutil.parser import parse
from corpus.eventcorpus import DataSource
from corpus.utils.DatePolarHistogram import DatePolarHistogram
from corpus.utils.plots import Histogramm, PlotSettings, Zipf, Plot
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
        labelPrefix="ordA"
        self.figureList=FigureList(caption="ordinal Histogramms",figureListLabel=f"{labelPrefix}-Hist")
        for dataSource in DataSource.sources.values():
            # loop over all datasources
            histOutputFileName=f"ordinalHistogramm-{dataSource.name}.png"
            zipfOutputFileName=f"ordinalHistogrammZipf-{dataSource.name}.png"
            try:
                print(f"creating histogramm for {dataSource}")
                maxValue=75 if dataSource in  ["tibkat","gnd"] else 50
                sqlQuery,lod=self.getLod(dataSource.tableName,maxValue=maxValue)
                figure=Figure(dataSource.title,caption=f"{dataSource.name} ordinals",figLabel=f"{labelPrefix}-{dataSource.name}",sqlQuery=sqlQuery,fileNames=[histOutputFileName,zipfOutputFileName])
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
                # set operation
                ordinals: List[int] = [int(r.get("ordinal"))
                                       for r in eventRecords
                                       if r.get("ordinal")
                                       and ((isinstance(r.get("ordinal"), str) and r.get("ordinal").isnumeric()) or isinstance(r.get("ordinal"), int))]
                if len(ordinals) == 0:
                    continue
                minOrd = min(ordinals)
                maxOrd = max(ordinals)
                numberOfDistinctOrds = len(set(ordinals))
                # count set content
                res = {
                    "series": series,
                    "minOrdinal": minOrd,
                    "maxOrdinal": maxOrd,
                    "avgOrdinal": mean(ordinals),
                    "completeness": numberOfDistinctOrds / maxOrd if maxOrd>1.0 else 1.0
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

    def testEventSignatureCompleteness(self):
        """
        event signature completeness of data sources
        """

        completeQuery = """SELECT COUNT(*) AS count
        FROM %s
        WHERE acronym is NOT NULL
        AND year is NOT NULL
        AND city is NOT NULL
        AND country is NOT NULL
        AND ordinal is NOT NULL
        AND title is NOT NULL
        AND startDate is NOT NULL
        """

        propertyQuery = """SELECT COUNT(*) AS count
        FROM %s
        WHERE %s is NOT NULL
        """
        totalRecordsQuery = "SELECT COUNT(*) AS count FROM %s"
        signatureProps = ["acronym", "startDate", "ordinal", "year", "title", "city", "country"]
        sqlDB = EventStorage.getSqlDB()
        res = {}
        self.figureList=FigureList(caption="datasource signature completeness",figureListLabel="signcomp",cols=2)
        for dataSource in DataSource.sources.values():
            if dataSource.name in ["acm", "ceurws", "or", "orbackup", "orclonebackup"]:
                continue
            try:
                total = sqlDB.query(totalRecordsQuery % (dataSource.tableName))[0].get("count")
                dataSourceCompletness = {
                    "complete": round(sqlDB.query(completeQuery % (dataSource.tableName))[0].get("count") / total, 2),
                    **{prop:round(sqlDB.query(propertyQuery % (dataSource.tableName, prop))[0].get("count")/total, 2) for prop in signatureProps}
                }
                print(dataSource, dataSourceCompletness)
                res[dataSource] = dataSourceCompletness
            except Exception as ex:
                print(f"{dataSource.name} signatureCompleteness failed")

        for prop in ["complete", *signatureProps]:
            values = [v.get(prop) for v in res.values()]

            plot = Plot()
            title = f"Event Signature Completeness - {prop}"
            plot.setup(title)

            labels = [dataSource.title for dataSource in res]

            x = np.arange(len(res.values()))  # the label locations
            width = 0.35  # the width of the bars


            fig, ax = plot.plt.subplots()
            rect = ax.bar(x, values, width, color=['#4c4cff'])
            ax.set_ylabel('Completeness')
            ax.set_title(title)
            ax.set_xticks(x, labels , rotation='vertical')
            ax.bar_label(rect, padding=3)
            fig.tight_layout()
            histOutputFileName=f"completeSignature_{prop}.png"
            ps = PlotSettings(outputFile=f"{self.histroot}/{histOutputFileName}")
            plot.doShow(ps)
            figure=Figure(dataSource.title,caption=f"signature completeness of {prop}",figLabel=f"signcomp-{prop}",sqlQuery=None,fileNames=[histOutputFileName])
            self.figureList.add(figure)
        self.figureList.printAllMarkups()

    def test_VolumeDistribution(self):
        """
        tests the volume distribution in tibkat
        """
        volumeRegexp = r'\[?[Vv]ol\.\]?( |)(?P<volumeNumber>\d{1,2}|[A-H]|(IX|IV|V?I{0,3}))'
        sqlQuery = """SELECT title FROM event_tibkat WHERE LOWER(title) LIKE "%vol.%" """
        sqlDB = EventStorage.getSqlDB()
        lod = sqlDB.query(sqlQuery)
        volumes = {}
        for d in lod:
            title = d.get('title')
            if title:
                match = re.search(volumeRegexp, title)
                if match is None:
                    continue
                volume = match.group("volumeNumber")
                if volume in volumes:
                    volumes[volume] += 1
                else:
                    volumes[volume] = 1
        totalRecords = sum(volumes.values())
        volumes = [(k,v) for k,v in volumes.items()]
        volumes.sort(key=lambda item:item[1], reverse=True)
        plot = Plot()
        title = f"Volume Number Distribution in Tibkat records"
        plot.setup(title)

        labels = [volNumber for (volNumber, count) in volumes]
        values = [count for (volNumber, count) in volumes]
        x = np.arange(len(values))  # the label locations
        width = 0.35  # the width of the bars

        fig, ax = plot.plt.subplots(figsize=[15,10])
        fig.suptitle(f"(#records in total: {totalRecords})")
        rect = ax.bar(x, values, width)
        ax.set_ylabel('number of records')
        ax.set_xlabel('volume number')
        ax.set_title(title)
        ax.set_xticks(x, labels, rotation='vertical')
        ax.legend()
        histOutputFileName = f"volumeNumberDistribution_tibkat.png"
        ps = PlotSettings(outputFile=f"{self.histroot}/{histOutputFileName}")
        plot.doShow(ps)
        print(volumes)

    def testStartDateDistribution(self):
        """
        tests the startDate distribution
        Assumption: due to a parsing error it is expected that many events wrongfully are dated at the first of january
        """
        for source in list(DataSource.sources.values()):
            if source.name in ["acm", "ceurws", "or", "orbackup", "orclonebackup"]:
                continue
            with self.subTest(source=source):
                sqlQuery = f"""SELECT startDate FROM {source.tableName}"""
                sqlDB = EventStorage.getSqlDB()
                lod = sqlDB.query(sqlQuery)
                rawDates = [d.get("startDate") for d in lod]
                dates = []
                for date in rawDates:
                    if isinstance(date, datetime.datetime) or isinstance(date, datetime.date):
                        dates.append(date)
                    elif isinstance(date, str):
                        dates.append(parse(date))
                    else:
                        if date is not None:
                            print(f"{source.name}: ", "Filtered out", date, f"(Type:{type(date)})")
                print("Filtered out", len(lod)-len(dates), "due to wrong format")
                hist = DatePolarHistogram(dates)
                hist.plt.title(f"Histogram of Event startDates in {source.name}")
                #hist.plot()
                histOutputFileName = f"startDate_histogram_{source.name}.png"
                ps = PlotSettings(outputFile=f"{self.histroot}/{histOutputFileName}")
                hist.doShow(ps)
