'''
Created on 2022-02-16

@author: wf
'''
import corpus
from dataclasses import dataclass

@dataclass
class Version():
    '''
    Version handling for ConferenceCorpus
    '''
    name = "Conference Corpus Browser"
    description = 'Conference Corpus Volume browser'
 
    version=corpus.__version__
    date = '2020-09-10'
    updated = '2024-02-04'
    
    doc_url="https://wiki.bitplan.com/index.php/ConferenceCorpus"
    chat_url="https://github.com/WolfgangFahl/ConferenceCorpus/discussions"
    cm_url="https://github.com/WolfgangFahl/ConferenceCorpus"

    authors = 'Wolfgang Fahl, Tim Holzheim'
    license = f'''Copyright 2020-2024 contributors. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.'''
    longDescription = f"""{name} version {version}
{description}

  Created by {authors} on {date} last updated {updated}"""

        