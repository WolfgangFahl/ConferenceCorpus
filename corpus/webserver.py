'''
Created on 2021-01-01

@author: wf
'''
from fb4.app import AppWrap
from fb4.widgets import Copyright, Link,Menu, MenuItem
from flask import flash,render_template, url_for
import os
import socket
import sys
from corpus.lookup import CorpusLookup

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
        template_folder=scriptdir + '/../templates'
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
        
    def initLookup(self):
        '''
        init my corpus lookup
        '''
        self.lookup=CorpusLookup()
        # TODO add lookupId handling for pre loaded data
        #lookup.load(forceUpdate=False,showProgress=True)
        self.queryManager=self.lookup.getQueryManager()
        
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
        flash(f"query {name}")
        template="cc/table.html"
        activeItem="Queries"
        title=f"Conference Corpus Query {name}"
        lodKeys=[]
        if name not in self.queryManager.queriesByName:
            flash(f"unknown query {name}","warn")
            qlod=[]
        else:
            query=self.queryManager.queriesByName[name]
            qlod=self.lookup.getLod4Query(query.query)
            lodKeys=qlod[0].keys()
        html=render_template(template, title=title, activeItem=activeItem,dictList=qlod,lodKey=lodKeys,tableHeaders=lodKeys)
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