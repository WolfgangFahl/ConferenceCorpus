import pathlib
import os
from setuptools import setup
from collections import OrderedDict
from corpus.version import Version

try:
    long_description = ""
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()

except:
    print('Curr dir:', os.getcwd())
    long_description = open('../../README.md').read()
here = pathlib.Path(__file__).parent.resolve()
requirements = (here / 'requirements.txt').read_text(encoding='utf-8').split("\n")

setup(name='ConferenceCorpus',
      version=Version.version,
      description='python api providing access to academic events and event series from different sources',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://wiki.bitplan.com/index.php/ConferenceCorpus',
      download_url='https://github.com/WolfgangFahl/ConferenceCorpus',
      author='Wolfgang Fahl',
      author_email='wf@bitplan.com',
      license='Apache',
      project_urls=OrderedDict(
        (
            ("Code", "https://github.com/WolfgangFahl/ConferenceCorpus"),
            ("Issue tracker", "https://github.com/WolfgangFahl/ConferenceCorpus/issues"),
        )
      ),
      classifiers=[
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10'
      ],
      packages=['resources','corpus','corpus.datasources','corpus.utils','corpus.quality','corpus.xmlhandler', 'corpus.matching','ptp'],
      package_data={'resources':['*.yaml', '*.json', 'matching/*.json']},
      install_requires=requirements,
      entry_points={
         'console_scripts': [
             'aelookup = corpus.lookup:main',
             'ccTibkat = corpus.datasources.tibkatftx:main',
             'ccUpdate = corpus.ccupdate:main'
      ],
    },
      zip_safe=False)
