"""
Created on 22.11.2023

@author: wf

This module contains tests for querying the Conference Corpus.

The `TestConferenceCorpusQueries` class extends `Basetest` and provides
methods to test queries against the Conference Corpus. It particularly focuses
on the ability to generate HTML markup from the corpus queries.
"""

from ngwidgets.basetest import Basetest
from corpus.web.cc_queries import ConferenceCorpusQueries

class TestConferenceCorpusQueries(Basetest):
    """Test class for querying the Conference Corpus.

    This class tests the functionality of ConferenceCorpusQueries,
    specifically its ability to convert query results to HTML format.
    """

    def test_cc_queries(self) -> None:
        """
        Test the generation of HTML markup from conference corpus queries.

        This method checks if the ConferenceCorpusQueries can successfully
        convert its query results into HTML format and contains specific
        HTML tags indicating a successful conversion.
        """
        ccq = ConferenceCorpusQueries()
        markup = ccq.as_html()
        debug = self.debug
        # Uncomment the next line to enable debugging output
        # debug = True
        if debug:
            print(markup)
        self.assertTrue("<li><a" in markup)  # Checking for specific HTML tag in output
