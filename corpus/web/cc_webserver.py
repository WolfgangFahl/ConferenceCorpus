"""
Created on 2023-11-18

@author: wf
"""
from ngwidgets.input_webserver import InputWebserver
from ngwidgets.webserver import WebserverConfig
from corpus.version import Version
from nicegui import ui, Client
from ngwidgets.profiler import Profiler
from corpus.eventcorpus import DataSource

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
        
    async def home(self, _client: Client):
        """
        provide the main content page
        """
        await(self.setup_content_div(self.setup_home))