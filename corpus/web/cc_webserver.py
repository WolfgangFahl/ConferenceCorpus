"""
Created on 2023-11-18

@author: wf
"""
from ngwidgets.input_webserver import InputWebserver, InputWebSolution
from ngwidgets.webserver import WebserverConfig
from corpus.version import Version
from nicegui import app,ui, Client
from ngwidgets.profiler import Profiler
from corpus.eventcorpus import DataSource
from corpus.lookup import CorpusLookup
from corpus.web.eventseries import EventSeriesAPI
from corpus.web.cc_stats import Dashboard
from corpus.web.cc_queries import ConferenceCorpusQueries

class ConferenceCorpusWebserver(InputWebserver):
    """
    Webserver for the Conference Corpus
    """
    
    @classmethod
    def get_config(cls) -> WebserverConfig:
        """
        get the configuration for this Webserver
        """
        copy_right = "(c)2020-2024 Wolfgang Fahl"
        config = WebserverConfig(
            short_name="cc",
            copy_right=copy_right, 
            version=Version(), default_port=5005
        )
        server_config=WebserverConfig.get(config)
        server_config.solution_class=ConferenceCorpusSolution
        return server_config
    
    def __init__(self):
        """Constructor"""
        InputWebserver.__init__(self, config=ConferenceCorpusWebserver.get_config())
        self.lookup=CorpusLookup()
        self.event_series_api=EventSeriesAPI(self.lookup)
        self.queries=ConferenceCorpusQueries()
        
        @ui.page("/stats")
        async def stats(client:Client):
            return await self.page(client,ConferenceCorpusSolution.show_stats_dashboard)
        
        @ui.page("/queries")
        async def show_queries(client:Client):
            return await self.page(client.ConfernceCorpusSolution.show_queries)
        
        @app.get('/eventseries/{name}')
        def get_eventseries(name: str, bks: str = "", reduce: bool = False, table_fmt: str = "json"):
            # Use the parameters directly in the API calls
            event_series_dict = self.event_series_api.getEventSeries(name, bks, reduce)
            response = self.event_series_api.convertToRequestedFormat(name, event_series_dict, table_fmt)
            return response
        
class ConferenceCorpusSolution(InputWebSolution):
    """
    Conference Corpus per Client Web UI
    """
    def __init__(self, webserver:ConferenceCorpusWebserver, client: Client):
        super().__init__(webserver, client)  # Call to the superclass constructor
         
    def setup_home(self):
        """
        first load all data sources then
        show a table of these
        """
        msg="loading datasources ..."
        self.loading_msg=ui.html(msg)
        profiler=Profiler(msg,profile=False)
        DataSource.getAll()
        elapsed=profiler.time()
        data_sources=DataSource.sources.values()
        msg=f"{len(data_sources)} datasources loaded in {elapsed*1000:5.0f} msecs"
        self.loading_msg.content=msg
        for index,source in enumerate(data_sources,start=1):
            ui.label(f"{index}:{source.title}")
        pass
    
    async def show_stats_dashboard(self):
        """
        show the statistics dashboard
        """
        def show():
            self.dashboard=Dashboard(self)
        await self.setup_content_div(show)
        
    async def show_queries(self):
        """
        show the list of available queries
        """
        def show():
            ui.html(self.queries.as_html())
        await self.setup_content_div(show)
   
    
    def configure_menu(self):
        """
        add a menu entry
        """
        self.link_button(name="statistics",target="/stats",icon_name="query_stats")
        
    async def home(self):
        """
        provide the main content page
        """
        await(self.setup_content_div(self.setup_home))