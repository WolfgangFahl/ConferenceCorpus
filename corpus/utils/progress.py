'''
Created on 2022-03-05

@author: wf
'''

class Progress(object):
    '''
    Progress Display
    '''

    def __init__(self,progressSteps:int=None):
        '''
        Constructor
        
        Args:
            progressSteps(int): show progress after the given number of steps
        '''
        self.count=0
        self.progressSteps=progressSteps
        
    def next(self):
        '''
        count the progress and show it
        '''
        self.count+=1
        if self.progressSteps is not None:
            if self.count%self.progressSteps==0:
                    print(".",flush=True,end='')
            if self.count%(self.progressSteps*80)==0:
                    print(f"\n{self.count}",flush=True)
        