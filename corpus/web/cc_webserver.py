"""
Created on 2023-11-18

@author: wf
"""
from ngwidgets.input_webserver import InputWebserver
from ngwidgets.webserver import WebserverConfig
from corpus.version import Version

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
 
