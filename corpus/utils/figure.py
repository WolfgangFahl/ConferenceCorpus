'''
Created on 19.05.2022

@author: wf
'''
class Figure():
    '''
    a figure 
    '''
    def __init__(self,title,caption,figLabel,sqlQuery,fileNames,px=600,scale=0.5):
        '''
        constructore
        '''
        self.title=title
        self.caption=caption
        self.sqlQuery=sqlQuery
        self.figLabel=figLabel
        self.fileNames=fileNames
        self.px=px
        self.scale=scale
        
    def asWikiMarkup(self):
        '''
        create mediawiki markup to show the given outputFilename and sqlQuery
        '''
        markup=f"""== {self.title} =="""
        if self.sqlQuery:
            markup+=f"""
=== sql query ===
<source lang='sql'>
{self.sqlQuery}
</source>"""
        markup+=f"""
=== {self.caption} ===
"""
        for fileName in self.fileNames:
            markup+=f"""[[File:{fileName}|{self.px}px]]"""
        return markup 
    
    def asLatex(self):
        '''
        get the latex Code for the given figure
        '''
        latex="""\\begin{figure}
    \centering
        """
        for fileName in self.fileNames:
            latex+="""{\includegraphics[scale=%s]{%s}}""" % (self.scale,fileName)
        latex+="""
    \caption{%s}
    \label{fig:%s}
\end{figure}"""
        return latex % (self.caption,self.figLabel)
    
class FigureList():
    '''
    Figure List
    '''
    def __init__(self):
        self.figures=[]
        
    def add(self,figure:Figure):
        self.figures.append(figure)
    
    def printAllMarkups(self):
        for figure in self.figures:
            print(figure.asWikiMarkup())
        for figure in self.figures:
            print(figure.asLatex())