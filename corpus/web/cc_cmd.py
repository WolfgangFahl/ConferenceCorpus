'''
Created on 2023-09-10

@author: wf
'''
import sys
from ngwidgets.cmd import WebserverCmd
from corpus.web.cc_webserver import ConferenceCorpusWebserver
class ConferenceCorpusCmd(WebserverCmd):
    """
    command line handling for Conference Corpus Webserver
    """
    
def main(argv:list=None):
    """
    main call
    """
    cmd=ConferenceCorpusCmd(config=ConferenceCorpusWebserver.get_config(),webserver_cls=ConferenceCorpusWebserver)
    exit_code=cmd.cmd_main(argv)
    return exit_code
        
DEBUG = 0
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(main())