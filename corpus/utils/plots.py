'''
Created on 2022-05-17

@author: wf
'''
import io
import matplotlib.pyplot as plt
import numpy as np
import statistics
from typing import Callable
from collections import Counter
from scipy.optimize import minimize 

class PlotSettings():
    '''
    plot settings
    '''
    def __init__(self,imageFormat='png',interactive:bool=False,outputFile:str=None,callback:Callable=None):
        '''
        Constructor 
        
        Args:
            imageFormat(str): the format for the outputFile
            interactive(bool): if True show using matplotlib backend
            outputFile(str): the path to the outputfile
            callback(Callable): optional function to call to set more details of figure/plot
        '''
        self.imageFormat=imageFormat
        self.interactive=interactive
        self.outputFile=outputFile
        self.callback=callback
        
            
class Plot():
    '''
    super class of all plots
    '''
    def __init__(self):
        pass
    
    def setup(self,title:str):
        '''
        setup my figure and  plot (is global anyway but shouldn't be ...)
        
        Args:
            title(str)
        '''
        self.fig = plt.figure(title)
        self.plt = plt
        # clear
        plt.clf()
        plt.title(title)
    
    def doShow(self,ps:PlotSettings=None):
        '''
        '''
        if not ps:
            return
        if ps.callback:
            ps.callback(self)
        if ps.interactive and not ps.outputFile:
            self.plt.show()
            return None
        else:
            if ps.outputFile is None:
                ps.outputFile = io.BytesIO()
            self.plt.savefig(ps.outputFile, format=ps.imageFormat,dpi=self.fig.dpi)
            plt.close(self.fig)
            return ps.outputFile

class Zipf(Plot):
    '''
    https://stats.stackexchange.com/questions/331219/characterizing-fitting-word-count-data-into-zipf-power-law-lognormal
    https://stats.stackexchange.com/questions/6780/how-to-calculate-zipfs-law-coefficient-from-a-set-of-top-frequencies
    https://stackoverflow.com/questions/12037494/curve-fitting-zipf-distribution-matplotlib-python
    
    '''
    def __init__(self, values):
        self.values=values
        self.counter_of_values = Counter(self.values)
        self.mean = statistics.mean(self.counter_of_values.values())
        self.x=np.array(list(self.counter_of_values.keys()))
        self.freqs=np.array(list(self.counter_of_values.values())) 
        
        
    def fit(self):
        '''
        calculate the zipf distribution fit
        '''
        def loglik(b):  
            # Power law function
            Probabilities = self.x**(-b)
        
            # Normalized
            Probabilities = Probabilities/Probabilities.sum()
        
            # Log Likelihoood
            # Lvector = np.log(Probabilities)
        
            # Multiply the vector by frequencies
            Lvector = np.log(Probabilities) * self.freqs
        
            # LL is the sum
            L = Lvector.sum()
        
            # We want to maximize LogLikelihood or minimize (-1)*LogLikelihood
            return(-L)

        fitResult=minimize(loglik, [2]) 
        return fitResult

        
    def show(self,title:str="Power law",ps:PlotSettings=None):
       
        #counter_of_counts = Counter(counter_of_values.values())
        #value_counts = np.array(list(counter_of_counts.keys()))
        #freq_of_value_counts = np.array(list(counter_of_counts.values()))
        #plt.scatter(np.log(value_counts), np.log(freq_of_value_counts))
        self.setup(title)
        plt.scatter(
            self.x,
            np.log(self.freqs),       
        )
        plt.xlabel('Values')
        plt.ylabel('Log of count')
        fit=self.fit()
        sx=3
        sy=self.mean
        if fit.success:
            plt.text(sx, sy, r'Zipf distribution fit $\mu=100,\ \sigma=15$')
        else:
            plt.text(sx, sy, r'no Zipf distribution fit')
        self.doShow(ps)
        

class Histogramm(Plot):
    '''
    Histogramm
    '''

    def __init__(self, x):
        self.x=x
    
    def show(self,xLabel,yLabel,title,facecolor='b',alpha=0.5,grid:bool=True,ps:PlotSettings=None):
        '''
        show the histogramm
        
        Args:
            xLabel(str): the x-axis label
            yLabel(str): the y-axis label
            title(str): the title
            facecolor(str): the facecolor to use
            alpha(float): how opaque
            grid(bool): if True show the histogramm grid
            ps(PlotSettings): plot settings
            
        '''
        # the histogram of the data
        self.setup(title)
    
        bins = np.arange( min( self.x ) - 0.5 ,
                     max( self.x ) + 1.5 , 1.0 ) 
        _n, _bins, _patches = plt.hist(self.x, bins, density=False, facecolor=facecolor, alpha=alpha)
    
        plt.xlabel(xLabel)
        plt.ylabel(yLabel)
        plt.grid(grid)
        self.doShow(ps)
        
            