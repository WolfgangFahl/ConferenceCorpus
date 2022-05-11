'''
Created on 2021-01-01

@author: wf
'''
from fb4.app import AppWrap
from fb4.widgets import Copyright, Link, Menu, MenuItem, LodTable
from flask import flash, render_template, url_for, request, jsonify
from werkzeug.exceptions import HTTPException
import os
import socket
import sys
import traceback
from corpus.lookup import CorpusLookup
from corpus.event import EventStorage
#from corpus.web.eventseriesblueprint import EventSeriesBlueprint
from corpus.web.scholar import ScholarBlueprint


class WebServer(AppWrap):
    """
    ConferenceCorpus WebService
    """

    def __init__(self, host=None, port=5005, verbose=True, debug=False):
        '''
        constructor

        Args:
            host(str): flask host
            port(int): the port to use for http connections
            debug(bool): True if debugging should be switched on
            verbose(bool): True if verbose logging should be switched on
        '''
        self.debug = debug
        self.verbose = verbose
        scriptdir = os.path.dirname(os.path.abspath(__file__))
        template_folder=scriptdir + '/../../templates'
        if host is None:
            host=socket.gethostname()
        super().__init__(host=host, port=port, debug=debug, template_folder=template_folder)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.app_context().push()
        self.authenticate=False
        
        #  server specific initializations
        link=Link("http://www.bitplan.com/Wolfgang_Fahl",title="Wolfgang Fahl")
        self.copyRight=Copyright(period="2021-2022",link=link)
        self.initLookup()

        #Blueprints
        self.scholarBlueprint=ScholarBlueprint(self.app, "scholar", template_folder="scholar", appWrap=self)
        #self.eventSeriesBlueprint = EventSeriesBlueprint(self.app, "eventseries", template_folder="eventseries", appWrap=self)
 
        @self.app.route('/')
        def home():
            return self.homePage()   
        
        @self.app.route('/datasources')
        def datasources():
            return self.showDataSources() 
        
        @self.app.route('/queries')
        def queries():
            return self.showQueries() 
        
        @self.app.route('/query/<name>')
        def query(name:str):
            return self.showQuery(name)
        
        @self.app.route('/eventseries/<name>')
        def getEventSeries(name: str):
            return self.getEventSeries(name)

        @self.app.errorhandler(Exception)
        def handle_exception(e):
            # pass through HTTP errors
            if isinstance(e, HTTPException):
                return e
            traceMessage = traceback.format_exc()
            # to the server log
            print(traceMessage,flush=True)
            errorMessage=f"A server error occurred - see log for trace"
            
            return self.handleError(errorMessage)


    def handleError(self,errorMessage,level="error"):   
        '''
        handle the error with the given error Message
        '''     
        flash(errorMessage,level)
        # now you're handling non-HTTP exceptions only
        html=self.render_template("cc/generic500.html", title="Error", activeItem="Home", error=errorMessage)
        return html
        
    def initLookup(self):
        '''
        init my corpus lookup
        '''
        self.lookup=CorpusLookup()
        # TODO add lookupId handling for pre loaded data
        #lookup.load(forceUpdate=False,showProgress=True)
        self.queryManager=EventStorage.getQueryManager()
        
    def render_template(self,templateName:str,title:str,activeItem:str,**kwArgs):
        '''
        render the given template with the default arguments
        
        Args:
            templateName(str): the name of the template to render
            title(str): the title to display for html
            activeItem(str): the name of the menu item to display as active
        '''
        html=render_template(templateName,title=title,menu=self.getMenu(activeItem),copyright=self.copyRight,**kwArgs)
        return html
        
    def homePage(self): 
        '''
        render the homepage
        '''
        template="cc/home.html"
        title="Conference Corpus"
        activeItem="Home"
        
        html=self.render_template(template, title=title, activeItem=activeItem)
        return html
    
    def showDataSources(self):
        '''
        show the datasources
        '''
        template="cc/datasources.html"
        title="Data Sources"
        activeItem=title
        html=self.render_template(template, title=title, activeItem=activeItem)
        return html
    
    def showQueries(self):
        '''
        show the available queries for selection
        '''
        template="cc/queries.html"
        title="Conference Corpus Queries"
        activeItem="Queries"
        linkList=[]
        for queryName in self.queryManager.queriesByName:
            linkList.append(Link(self.basedUrl(url_for("query",name=queryName)),title=queryName))
        html=self.render_template(template, title=title, activeItem=activeItem,linkList=linkList)
        
        return html
    
    def showQuery(self,name):
        '''
        show the query with the given name
        
        Args:
            name(str): the name of the query to be shown
        '''
        if name not in self.queryManager.queriesByName:
            errorMessage=f"unknown query {name}"
            return self.handleError(errorMessage,"warn")
        else:
            query=self.queryManager.queriesByName[name]
            qlod=self.lookup.getLod4Query(query.query)
            dictOfLod={name:qlod}
            title=f"Conference Corpus Query {name}"
            return self.renderDictOfLod(dictOfLod,title=title)
        
    def getEventSeries(self, name:str):
        '''
        Query multiple datasources for the given event series

        Args:
            name(str): the name of the event series to be queried
        '''
        multiQuery="select * from {event}"
        idQuery = f"""select source,eventId from event where lookupAcronym like "%{name}%" order by year desc"""
        dictOfLod = self.lookup.getDictOfLod4MultiQuery(multiQuery, idQuery)
        return self.convertToRequestedFormat(dictOfLod)
    

    def convertToRequestedFormat(self, dictOfLods:dict):
        """
        Converts the given dicts of lods to the requested format.
        Supported formats: json, html
        Default format: json

        Args:
            dictOfLods: data to be converted

        Returns:
            Response
        """
        formatParam = request.values.get('format', "")
        if formatParam.lower() == "html":
            tables=[]
            for name, lod in dictOfLods.items():
                tables.append(LodTable(name=name, lod=lod))
            template = "cc/result.html"
            title = "Query Result"
            result="".join([str(t) for t in tables])
            html = self.render_template(template, title=title, activeItem="", result=result)
            return html
        else:
            return jsonify(dictOfLods)

    
    def renderDictOfLod(self,dictOfLod:dict,title):
        '''
        render a dict of list of dicts
        '''
        template="cc/table.html"
        activeItem="Queries"
        qlod=next(iter(dictOfLod.values()))
        lodKeys=qlod[0].keys()
        html=self.render_template(template, title=title, activeItem=activeItem,dictList=qlod,lodKey=lodKeys,tableHeaders=lodKeys)
        return html
        
    
    def getMenu(self,activeItem:str=None):
        '''
        get the list of menu items for the admin menu
        Args:
            activeItem(str): the active  menu item
        Return:
            list: the list of menu items
        '''
        menu=Menu()
        #self.basedUrl(url_for(
        menu.addItem(MenuItem("/","Home",mdiIcon="home"))
        menu.addItem(MenuItem(url_for("queries"),"Queries",mdiIcon="quiz")),
        menu.addItem(MenuItem(url_for("datasources"),"Data Sources",mdiIcon="arrow_circle_up")),
        
        menu.addItem(MenuItem('https://wiki.bitplan.com/index.php/ConferenceCorpus',"Docs",mdiIcon="description",newTab=True)),
        menu.addItem(MenuItem('https://github.com/WolfgangFahl/ConferenceCorpus','github',mdiIcon="reviews",newTab=True))
        if activeItem is not None:
            for menuItem in menu.items:
                if isinstance(menuItem,MenuItem):
                    if menuItem.title==activeItem:
                        menuItem.active=True
                    menuItem.url=self.basedUrl(menuItem.url)
        return menu
        
DEBUG = False

def main(_argv=None):
    '''main program.'''
    # construct the web application
    web=WebServer()
    
    parser = web.getParser(description="Conference Corpus Webserver")
    parser.add_argument('--verbose', default=True, action="store_true", help="should relevant server actions be logged [default: %(default)s]")
    parser.add_argument('-li','--lookupIds', nargs='+', help='which corpus parts should be loaded')
    args = parser.parse_args()
    web.optionalDebug(args)
    web.run(args)

if __name__ == '__main__':
    sys.exit(main())    