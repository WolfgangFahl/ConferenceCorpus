'''
Created on 2023-01-23

@author: wf
'''
import os
import sys
from corpus.version import Version
from corpus.eventcorpus import DataSource
from jpcore.compat import Compatibility;Compatibility(0,11,1)
from jpcore.justpy_config import JpConfig
script_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = script_dir+"/resources/static"
JpConfig.set("STATIC_DIRECTORY",static_dir)
# shut up justpy
JpConfig.set("VERBOSE","False")
JpConfig.setup()
from jpwidgets.bt5widgets import About,App

class ConferenceCorpusBrowser(App):
    """
    conference corpus  browser
    """
    
    def __init__(self,version):
        """
        Constructor
        
        Args:
            version(Version): the version info for the app
        """
        import justpy as jp
        self.jp=jp
        App.__init__(self, version)
        # see https://pictogrammers.github.io/@mdi/font/2.0.46/
        self.addMenuLink(text='Home',icon='home', href="/")
        self.addMenuLink(text='Sources',icon='database',href="/sources")
        self.addMenuLink(text='github',icon='github', href=version.cm_url)
        self.addMenuLink(text='Chat',icon='chat',href=version.chat_url)
        self.addMenuLink(text='Documentation',icon='file-document',href=version.doc_url)
        self.addMenuLink(text='Settings',icon='cog',href="/settings")
        self.addMenuLink(text='About',icon='information',href="/about")
        
        jp.Route('/settings',self.settings)
        jp.Route('/sources',self.data_sources)
        jp.Route('/about',self.about)
     
    def setupRowsAndCols(self):
        """
        setup the general layout
        """
        head_html="""<link rel="stylesheet" href="/static/css/md_style_indigo.css">"""
        self.wp=self.getWp(head_html)
        self.button_classes = """btn btn-primary"""
        # rows
        self.rowA=self.jp.Div(classes="row",a=self.contentbox)
        self.rowB=self.jp.Div(classes="row",a=self.contentbox)
        self.rowC=self.jp.Div(classes="row",a=self.contentbox)
        # columns
        self.colA1=self.jp.Div(classes="col-12",a=self.rowA)
        self.colB1=self.jp.Div(classes="col-6",a=self.rowB)
        self.rowB1r1=self.jp.Div(classes="row",a=self.colB1)
        self.colB11=self.jp.Div(classes="col-3",a=self.rowB1r1)
        self.rowB1r2=self.jp.Div(classes="row",a=self.colB1)
        self.colB12=self.jp.Div(classes="col-6",a=self.rowB1r2)
        self.colB2=self.jp.Div(classes="col-6",a=self.rowB)
        self.colC1=self.jp.Div(classes="col-12",a=self.rowC,style='color:black')
        # standard elements
        self.errors=self.jp.Div(a=self.colA1,style='color:red')
        self.messages=self.jp.Div(a=self.colC1,style='color:black')    
        
    async def settings(self)->"jp.WebPage":
        '''
        settings
        
        Returns:
            jp.WebPage: a justpy webpage renderer
        '''
        self.setupRowsAndCols()
        return self.wp
    
    def getSourcesTable(self)->str:
        """
        get the table of data sources
        """
        DataSource.getAll()
        markup="""<table class="table">
    <thead class="primary">
        <tr>
            <th scope="col">#</th>
            <th scope="col">Source</th>
            <th scope="col">mode</th>
            <th scope="col">events</th>
            <th scope="col">acronyms</th>
         </tr>
    </thead>
    <tbody>
    """
        acronymCount=0
        eventsCount=0
        for index,source in enumerate(DataSource.sources.values()):
            markup+=f"""<tr>
    <th scope="row">{index+1}</th>
    <td>{source.title}
            </tr>
            """
        #   <td><a href='{{em.url}}' title='{{em.title}}'>{{em.title}}</a></td>
        #<td>{{em.storeMode().name}}</td>
        #<td  style="text-align:right">{{ em.events|length }} </td>
        #<td  style="text-align:right">{{ em.eventsByAcronym|length }} </td>
        markup+=f"""<tr>
                 <th scope="row">∑</th>
                 <td></td>
                 <td></td>
                 <td style="text-align:right">{eventsCount}</td>
                 <td style="text-align:right">{acronymCount}</td>
           </tr>"""
        markup+="""</tbody>
        </table>
        """
        return markup
    
    async def data_sources(self)->"jp.WebPage":
        '''
        sources
        
        Returns:
            jp.WebPage: a justpy webpage renderer
        '''
        self.setupRowsAndCols()
        self.sourcesDiv=self.colB1
        self.sourcesDiv.inner_html=self.getSourcesTable()
        return self.wp

    async def about(self)->"jp.WebPage":
        '''
        show about dialog
        
        Returns:
            jp.WebPage: a justpy webpage renderer
        '''
        self.setupRowsAndCols()
        self.aboutDiv=About(a=self.colB1,version=self.version)
        # @TODO Refactor to pyJustpyWidgets
        return self.wp
        
    async def content(self)->"jp.WebPage":
        '''
        provide the main content page
        
        Returns:
            jp.WebPage: a justpy webpage renderer
        '''
        self.setupRowsAndCols()
        return self.wp
    
DEBUG = 0
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    app=ConferenceCorpusBrowser(Version)
    sys.exit(app.mainInstance())
