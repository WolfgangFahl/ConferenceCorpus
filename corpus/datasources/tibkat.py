'''
Created on 2022-02-16

@author: wf
'''
from corpus.version import Version
import json
import os
import sys
DEBUG = 0
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

class Tibkat:
    '''
    TIBKAT event meta data access
    
    https://www.tib.eu
    
    Technische Informationsbibliothek (TIB)
    
    Public datasets available via
    
    https://tib.eu/data/rdf
    
    '''
    
    def main(self,args):
        '''
        command line access
        '''
        # should take json import and modify target wiki
        
    
    
def main(argv=None): # IGNORE:C0111
    '''main program.'''

    if argv is None:
        argv=sys.argv[1:]
        
    program_name = os.path.basename(__file__)
    program_version = "v%s" % Version.version
    program_build_date = str(Version.updated)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = "script import TIBKat Data into openresearch compatible wiki"
    user_name="Wolfgang Fahl/Tim Holzheim"
    program_license = '''%s

  Created by %s on %s.
  Copyright 2022 contributors. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc,user_name, str(Version.date))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-d", "--debug", dest="debug",   action="store_true", help="set debug [default: %(default)s]")
        parser.add_argument("-t", "--target", dest="target", help="target wiki id")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        args = parser.parse_args(argv)
        tibkat=Tibkat()
        tibkat.main(args)
     
  
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 1
    except Exception as e:
        if DEBUG:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2     

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(main())
