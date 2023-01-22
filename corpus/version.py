'''
Created on 2022-02-16

@author: wf
'''

class Version(object):
    '''
    Version handling for ConferenceCorpus
    '''
    name = "Conference Corpus Browser"
    description = 'Conference Corpus Volume browser'
 
    version='0.1.2'
    date = '2020-09-10'
    updated = '2023-01-22'
    
    doc_url="https://wiki.bitplan.com/index.php/ConferenceCorpus"
    chat_url="https://github.com/WolfgangFahl/ConferenceCorpus/discussions"
    cm_url="https://github.com/WolfgangFahl/ConferenceCorpus"

    authors = 'Wolfgang Fahl, Tim Holzheim'
    license = f'''Copyright 2022-2023 contributors. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.'''
    longDescription = f"""{name} version {version}
{description}

  Created by {authors} on {date} last updated {updated}"""

        