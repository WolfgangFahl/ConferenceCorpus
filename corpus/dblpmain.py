'''
Created on 2022-03-05

@author: wf
'''
import os
import sys
import traceback
from corpus.version import Version
from corpus.lookup import CorpusLookup
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

def main(argv=None): # IGNORE:C0111
    '''main program.'''

    if argv is None:
        argv=sys.argv[1:]
        
    program_name = os.path.basename(__file__)
    program_version = "v%s" % Version.version
    program_build_date = str(Version.updated)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = "dblp xml handling from command line"
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
        parser.add_argument("-u", "--update", dest="update",   action="store_true", help="update the dblp xml file and eventcorpus database")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        args = parser.parse_args(argv)
        if args.update:
            lookup=CorpusLookup(lookupIds=["dblp"])
            lookup.load(forceUpdate=True)
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 1
    except Exception as e:
        if DEBUG:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        if args.debug:
            print(traceback.format_exc())
        return 2     
        
DEBUG = 0
    
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(main())
