"""
Created on 2023-11-18

@author: wf
"""
from ngwidgets.input_webserver import InputWebserver
from ngwidgets.webserver import WebserverConfig
from corpus.version import Version
from nicegui import app,ui, Client
from ngwidgets.profiler import Profiler
from corpus.eventcorpus import DataSource
from corpus.lookup import CorpusLookup
from corpus.web.eventseries import EventSeriesAPI
from corpus.web.cc_stats import Dashboard
    
class ConferenceCorpusWebserver(InputWebserver):
    """
    Webserver for the Conference Corpus
    """
    
    @classmethod
    def get_config(cls) -> WebserverConfig:
        """
        get the configuration for this Webserver
        """
        copy_right = "(c)2020-2023 Wolfgang Fahl"
        config = WebserverConfig(
            copy_right=copy_right, version=Version(), default_port=5005
        )
        return config
    
    def __init__(self):
        """Constructor"""
        InputWebserver.__init__(self, config=ConferenceCorpusWebserver.get_config())
        self.lookup=CorpusLookup()
        self.event_series_api=EventSeriesAPI(self.lookup)
        
        @ui.page("/stats")
        async def stats(client:Client):
            return await self.show_stats_dashboard()
        
        @app.get('/eventseries/{name}')
        def get_eventseries(name: str, bks: str = "", reduce: bool = False, format: str = "json"):
            # Use the parameters directly in the API calls
            event_series_dict = self.event_series_api.getEventSeries(name, bks, reduce)
            response = self.event_series_api.convertToRequestedFormat(name, event_series_dict, format)
            return response
        
    def handle_exception(self,ex):
        super().handle_exception(ex, trace=True)
 
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
    
    def configure_menu(self):
        """
        add a menu entry
        """
        self.link_button(name="statistics",target="/stats",icon_name="query_stats")
        
    async def home(self, _client: Client):
        """
        provide the main content page
        """
        await(self.setup_content_div(self.setup_home))