'''
Created on 17.05.2022

@author: wf
'''
from corpus.utils.plots import Histogramm, PlotSettings, Zipf
from tests.basetest import BaseTest
from corpus.event import EventStorage
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