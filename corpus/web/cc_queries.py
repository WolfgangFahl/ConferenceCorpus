"""
Created on 2023-11-22

@author: wf
"""

from ngwidgets.widgets import Link
from corpus.eventcorpus import EventStorage

class ConferenceCorpusQueries:
    """
    Class for managing and displaying queries related to a conference corpus.

    This class provides functionalities for accessing and rendering queries 
    related to conference data stored in an EventStorage system.
    """

    def __init__(self):
        """
        Initialize the ConferenceCorpusQueries instance.

        Sets up the query manager by retrieving it from the EventStorage.
        """
        self.queryManager = EventStorage.getQueryManager()  # Type: QueryManager
    
    def as_html(self) -> str:
        """
        Generate an HTML representation of the queries.

        Iterates through the available queries and creates an HTML unordered list 
        with links to each query.

        Returns:
            str: HTML string representing the list of queries.
        """
        markup = "<ul>"
        for queryName in self.queryManager.queriesByName:
            url = f"/query/{queryName}"
            link = Link.create(url, queryName,url_encode=True)
            markup += f"\n  <li>{link}"
        markup += "\n</ul>"
        return markup