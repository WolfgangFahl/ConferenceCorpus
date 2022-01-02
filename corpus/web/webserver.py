'''
Created on 2021-01-01

@author: wf
'''
from fb4.app import AppWrap
from fb4.widgets import Link,Menu, MenuItem
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
        template_folder=f"{scriptdir}/templates"
        if host is None:
            host=socket.gethostname()
        super().__init__(host=host, port=port, debug=debug, template_folder=template_folder)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.app_context().push()
        self.authenticate=False
        self.initLookup()
 
        @self.app.route('/')
        def home():
            return self.homePage()   
        
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
        
        
    def homePage(self): 
        '''
        render the homepage
        '''
        template="cc/home.html"
        title="Conference Corpus"
        
        html=render_template(template, title=title, menu=self.getMenuList())
        return html
    
    def showQueries(self):
        '''
        show the available queries for selection
        '''
        template="cc/queries.html"
        title="Conference Corpus Queries"
        linkList=[]
        for queryName in self.queryManager.queriesByName:
            linkList.append(Link(self.basedUrl(url_for("query",name=queryName)),title=queryName))
        html=render_template(template, title=title, menu=self.getMenuList(),linkList=linkList)
        
        return html
    
    def showQuery(self,name):
        '''
        
        '''
        flash(f"query {name}")
        template="cc/table.html"
        title=f"Conference Corpus Query {name}"
        lodKeys=[]
        if name not in self.queryManager.queriesByName:
            flash(f"unknown query {name}","warn")
            qlod=[]
        else:
            query=self.queryManager.queriesByName[name]
            qlod=self.lookup.getLod4Query(query.query)
            lodKeys=qlod[0].keys()
        html=render_template(template, title=title, menu=self.getMenuList(),dictList=qlod,lodKey=lodKeys,tableHeaders=lodKeys)
        return html
    
    def getMenuList(self,activeItem:str=None):
        '''
        get the list of menu items for the admin menu
        Args:
            activeItem(str): the active  menu item
        Return:
            list: the list of menu items
        '''
        menu=Menu()
        #self.basedUrl(url_for(
        menu.addItem(MenuItem("/","Home"))
        menu.addItem(MenuItem('https://wiki.bitplan.com/index.php/ConferenceCorpus/queries',"Queries")),
        menu.addItem(MenuItem('https://wiki.bitplan.com/index.php/ConferenceCorpus',"Docs")),
        menu.addItem(MenuItem('https://github.com/WolfgangFahl/ConferenceCorpus','github'))
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