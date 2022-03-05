'''
Created on 2022-03-05

@author: wf
'''
import time
from corpus.utils.download import Profiler
import getpass
import os

class Progress(object):
    '''
    Progress Display
    '''

    def __init__(self,progressSteps:int=None,expectedTotal:int=None,showDots:bool=False,msg:str=None):
        '''
        Constructor
        
        Args:
            progressSteps(int): show progress after each number of the given number steps
            expectedTotal(int): expectedTotal
            showDots(boolean): if True show dots (e.g. for log files) else show a proper progress bar
            msg(str): message to display (if any)
        '''
        self.count=0
        self.progressSteps=progressSteps
        self.expectedTotal=expectedTotal
        self.profiler=Profiler(msg=msg)
        self.startTime=self.profiler.starttime
        self.showDots=showDots or self.inCI()
        
    def inCI(self):
        '''
        are we running in a Continuous Integration Environment?
        '''
        publicCI=getpass.getuser() in ["travis", "runner"] 
        jenkins= "JENKINS_HOME" in os.environ
        return publicCI or jenkins
  
    def printProgressBar (self,iteration, total, prefix = '', suffix = '', decimals = 1, length = 72, fill = '█', printEnd = "\r",startTime=None):
        """
        Call in a loop to create terminal progress bar
        
        see https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
        
        Args:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        if startTime is None:
            print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
        else:
            elapsed=time.time()-startTime
            totalTime=elapsed*float(total)/iteration
            print(f'\r{prefix} |{bar}| {percent}% {elapsed:3.0f}/{totalTime:3.0f}s {suffix}', end = printEnd)
            
        # Print New Line on Complete
        if iteration == total: 
            print()
            
    def done(self):
        if self.progressSteps is not None:
            if self.showDots:
                print("!")
            else:
                self.printProgressBar(self.expectedTotal, self.expectedTotal,startTime=self.startTime)
        self.profiler.time()
        
    def next(self):
        '''
        count the progress and show it
        '''
        self.count+=1
        if self.progressSteps is not None:
            if self.showDots:   
                if self.count%self.progressSteps==0:
                    print(".",flush=True,end='')
                if self.count%(self.progressSteps*80)==0:
                    print(f"\n{self.count}",flush=True)
            else:
                if self.count%self.progressSteps==0:
                    self.printProgressBar(self.count, self.expectedTotal,startTime=self.startTime)