from setuptools import setup,find_packages
import os
from collections import OrderedDict

try:
    long_description = ""
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()

except:
    print('Curr dir:', os.getcwd())
    long_description = open('../../README.md').read()

setup(name='ConferenceCorpus',
      version='0.0.17',
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
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9'
      ],
      packages=['smw','corpus','datasources','quality'],
      install_requires=[
          'pylodstorage>=0.0.64',
          'python-dateutil',
          'py-3rdparty-mediawiki>=0.4.8',
          'wikirender>=0.0.24',
          'habanero'
      ],
      entry_points={
         'console_scripts': [
             'aelookup = corpus.lookup:main', 
      ],
    },
      zip_safe=False)
