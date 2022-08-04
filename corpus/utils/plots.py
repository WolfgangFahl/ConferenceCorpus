'''
Created on 2022-05-17

@author: wf
'''
import io
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from typing import Callable, List
from collections import Counter

import pandas as pd
from scipy.optimize import minimize
from scipy.optimize import curve_fit
from scipy.special import zetac

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
    def __init__(self, **kwargs):
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
    
    Powerlaw/Zipf Distribution plot and analysis
    
    https://stats.stackexchange.com/questions/331219/characterizing-fitting-word-count-data-into-zipf-power-law-lognormal
    https://stats.stackexchange.com/questions/6780/how-to-calculate-zipfs-law-coefficient-from-a-set-of-top-frequencies
    https://stackoverflow.com/questions/12037494/curve-fitting-zipf-distribution-matplotlib-python
    
    '''
    def __init__(self, values:list,minIndex:int=0):
        '''
        Constructor
        '''
        self.values=values
        self.counter_of_values = Counter(self.values)
        xValues=sorted(list(self.counter_of_values.keys()))
        xValues=xValues[minIndex:]
        self.x=np.array(xValues)
        yValues=[self.counter_of_values[x] for x in xValues]
        self.freqs=np.array(yValues) 
        self.mean = np.mean(self.freqs)
        self.freqsLog=np.log(self.freqs)
        self.freqsLogMean= np.mean(self.freqsLog)
        
    def curveFit(self):

        def f(x, a):
            return (x**-a)/zetac(a)


        result = curve_fit(f, self.x, self.freqs)
        return result

        
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
            self.freqsLog,       
        )
        plt.xlabel('Values')
        plt.ylabel('Log of count')
        fit=self.fit()
        curveFit=self.curveFit()
        sx=1
        sy=self.freqsLogMean-1
        if fit.success:
            s=fit.x[0]
            # https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
            popt,pcov=curveFit
            cfs=popt[0]
            #plt.text(sx, sy, fr'Zipf distribution fit s={s:.3f} cfs:{cfs:.3f} cov:{pcov}')
            #plt.plot(self.x, self.x*-s)
        else:
            plt.text(sx, sy, r'no Zipf distribution fit')
        self.doShow(ps)
        

class Histogramm(Plot):
    '''
    Histogram
    '''

    def __init__(self, x):
        self.x=x

    def prepareHistogram(self,facecolor='b',alpha=0.5,density:bool=False, bins=None, label=None):
        self.addHistogramSeries(x=self.x,
                                facecolor=facecolor,
                                alpha=alpha,
                                density=density,
                                bins=bins,
                                label=label)

    def addHistogramSeries(self, x, facecolor='b',alpha=0.5,density:bool=False, bins=None, label=None):
        if bins is None:
            bins = np.arange(min(x) - 0.5, max(x) + 1.5, 1.0)
        _n, _bins, _patches = plt.hist(x,
                                       bins,
                                       density=density,
                                       facecolor=facecolor,
                                       alpha=alpha,
                                       rwidth=0.9,
                                       label=label)
    
    def show(self,xLabel,yLabel,title,facecolor='b',alpha=0.5,density:bool=False,grid:bool=True,ps:PlotSettings=None,bins=None, vlineAt:int=None, label=None):
        '''
        show the histogram
        
        Args:
            xLabel(str): the x-axis label
            yLabel(str): the y-axis label
            title(str): the title
            facecolor(str): the facecolor to use
            alpha(float): how opaque
            density(bool): if True show the relative values
            grid(bool): if True show the histogramm grid
            ps(PlotSettings): plot settings
            
        '''
        # the histogram of the data
        self.setup(title)
        self.prepareHistogram(facecolor=facecolor,
                              alpha=alpha,
                              density=density,
                              bins=bins,
                              label=label)
        plt.xlabel(xLabel)
        plt.ylabel(yLabel)
        if density:
            yvals = plt.gca().get_yticks()
            #print(yvals)
            plt.gca().set_yticklabels([f"{y*100:.2f}%"for y in yvals])
        if vlineAt is not None:
            plt.gca().axvline(x=vlineAt, color='r', linestyle='dashed', linewidth=2)
        plt.grid(grid)
        plt.legend(loc='upper right')
        self.doShow(ps)


class HistogramSeries(Histogramm):
    '''
    Histogram of multiple Series
    '''

    def __init__(self, series:dict):
        if series is None:
            series = {}
        super().__init__(series)

    def addSeries(self, label:str, series):
        """
        Add a series to the histogram
        Args:
            label: label of the series (displayed in the legend)
            series: series data
        """
        self.x.update(label, series)

    def prepareHistogram(self, facecolor='b', alpha=0.5, density: bool = False, bins=None, label=None):
        """
        Prepares the histogram with the given parameters
        Args:
            facecolor:
            alpha:
            density:
            bins:
            label:

        Returns:

        """
        for i, (label, series) in enumerate(self.x.items()):
            color = list(mcolors.BASE_COLORS.keys())[i % len(mcolors.BASE_COLORS)]
            self.addHistogramSeries(x=series,
                                    facecolor=color,
                                    alpha=alpha,
                                    density=density,
                                    bins=bins,
                                    label=label)
        
            