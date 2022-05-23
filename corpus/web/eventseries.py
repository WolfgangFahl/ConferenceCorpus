from dataclasses import dataclass, field, asdict

from fb4.widgets import LodTable
from flask import Blueprint, request, jsonify, send_file
from iteration_utilities import flatten
from spreadsheet.spreadsheet import ExcelDocument

from corpus.datasources.openresearch import OREvent, OREventSeries
from corpus.eventseriescompletion import EventSeriesCompletion


class EventSeriesBlueprint():
    """
    API service for event series data
    """

    def __init__(self, app, name: str, template_folder:str=None, appWrap=None):
        '''
        construct me

        Args:
            name(str): my name
            template_folder(str): the template folder
        '''
        self.name = name
        if template_folder is not None:
            self.template_folder = template_folder
        else:
            self.template_folder = 'eventseries'
        self.blueprint = Blueprint(name, __name__, template_folder=self.template_folder,url_prefix="/eventseries")
        self.app = app
        self.appWrap = appWrap

        @self.blueprint.route('/<name>')
        def getEventSeries(name: str):
            return self.getEventSeries(name)

        app.register_blueprint(self.blueprint)

    def getEventSeries(self, name: str):
        '''
        Query multiple datasources for the given event series

        Args:
            name(str): the name of the event series to be queried
        '''
        multiQuery = "select * from {event}"
        idQuery = f"""select source,eventId from event where lookupAcronym LIKE "{name} %" order by year desc"""
        dictOfLod = self.appWrap.lookup.getDictOfLod4MultiQuery(multiQuery, idQuery)
        return self.convertToRequestedFormat(name, dictOfLod)

    def generateSeriesSpreadsheet(self, name:str, dictOfLods: dict) -> ExcelDocument:
        """

        Args:
            name(str): name of the series
            dictOfLods: records of the series from different sources

        Returns:
            ExcelDocument
        """
        spreadsheet = ExcelDocument(name=name)
        # Add completed event sheet and add proceedings sheet
        eventHeader = ["item", "label", "description", "Ordinal", "OrdinalStr", "Acronym", "Country", "City", "Title",
                       "Series", "Year", "Start date", "End date", "Homepage", "dblp", "dblpId", "wikicfpId", "gndId"]
        proceedingsHeaders = ["item", "label", "ordinal", "ordinalStr", "description", "Title", "Acronym",
                              "OpenLibraryId", "oclcId", "isbn13", "ppnId", "gndId", "dblpId", "doi", "Event",
                              "publishedIn"]
        eventRecords = list(flatten([lod for lod in dictOfLods.values()]))
        completedBlankEvent = EventSeriesCompletion.getCompletedBlankSeries(eventRecords)
        eventSheetRecords = []
        proceedingsRecords = []
        for year, ordinal in completedBlankEvent:
            eventSheetRecords.append({**{k: None for k in eventHeader}, "Ordinal": ordinal, "Year": year})
            proceedingsRecords.append({**{k: None for k in proceedingsHeaders}, "ordinal": ordinal})
        if not eventSheetRecords:
            eventSheetRecords = [{k: None for k in eventHeader}]
            proceedingsRecords = [{k: None for k in proceedingsHeaders}]
        spreadsheet.addTable("Event", eventSheetRecords)
        spreadsheet.addTable("Proceedings", proceedingsRecords)
        for lods in [dictOfLods, asdict(MetadataMappings())]:
            for sheetName, lod in lods.items():
                if isinstance(lod, list):
                    lod.sort(filter(lambda record: record.get('year',0) is not None),key=lambda record: record.get('year',0))
                spreadsheet.addTable(sheetName, lod)
        return spreadsheet

    def convertToRequestedFormat(self, name:str, dictOfLods: dict):
        """
        Converts the given dicts of lods to the requested format.
        Supported formats: json, html
        Default format: json

        Args:
            dictOfLods: data to be converted

        Returns:
            Response
        """
        formatParam = request.values.get('format', "")
        if formatParam.lower() == "html":
            tables = []
            for name, lod in dictOfLods.items():
                tables.append(LodTable(name=name, lod=lod))
            template = "cc/result.html"
            title = "Query Result"
            result = "".join([str(t) for t in tables])
            html = self.appWrap.render_template(template, title=title, activeItem="", result=result)
            return html
        elif formatParam.lower() == "excel":
                spreadsheet = self.generateSeriesSpreadsheet(name, dictOfLods)
                return send_file(spreadsheet.toBytesIO(), as_attachment=True, download_name=spreadsheet.filename, mimetype=spreadsheet.MIME_TYPE)
        else:
            return jsonify(dictOfLods)


@dataclass
class MetadataMappings:
    """
    Spreadsheet metadata mappings
    """
    WikidataMetadata: list = None
    SmwMetadata: list = None

    def __init__(self):
        self.WikidataMetadata = [{'Entity': 'Event series', 'Column':None, 'PropertyName': 'instanceof', 'PropertyId': 'P31', 'Value': 'Q47258130'},
             {'Entity': 'Event series', 'Column': 'Acronym', 'PropertyName': 'short name', 'PropertyId': 'P1813', 'Type': 'text'},
             {'Entity': 'Event series', 'Column': 'Title', 'PropertyName': 'title', 'PropertyId': 'P1476', 'Type': 'text'},
             {'Entity': 'Event series', 'Column': 'Homepage', 'PropertyName': 'official website', 'PropertyId': 'P856', 'Type': 'url'},
             {'Entity': 'Event', 'Column':None, 'PropertyName': 'instanceof', 'PropertyId': 'P31', 'Value': 'Q2020153'},
             {'Entity': 'Event', 'Column': 'Series', 'PropertyName': 'part of the series', 'PropertyId': 'P179'},
             {'Entity': 'Event', 'Column': 'Ordinal', 'PropertyName': 'series ordinal', 'PropertyId': 'P1545', 'Type': 'string', 'Qualifier': 'part of the series'},
             {'Entity': 'Event', 'Column': 'Acronym', 'PropertyName': 'short name', 'PropertyId': 'P1813', 'Type': 'text'},
             {'Entity': 'Event', 'Column': 'Title', 'PropertyName': 'title', 'PropertyId': 'P1476', 'Type': 'text'},
             {'Entity': 'Event', 'Column': 'Country', 'PropertyName': 'country', 'PropertyId': 'P17', 'Lookup': 'Q3624078'},
             {'Entity': 'Event', 'Column': 'City', 'PropertyName': 'location', 'PropertyId': 'P276', 'Lookup': 'Q515'},
             {'Entity': 'Event', 'Column': 'Start date', 'PropertyName': 'start time', 'PropertyId': 'P580', 'Type': 'date'},
             {'Entity': 'Event', 'Column': 'End date', 'PropertyName': 'end time', 'PropertyId': 'P582', 'Type': 'date'},
             {'Entity': 'Event', 'Column': 'gndId', 'PropertyName': 'GND ID', 'PropertyId': 'P227', 'Type': 'extid'},
             {'Entity': 'Event', 'Column': 'dblpUrl', 'PropertyName': 'describedAt', 'PropertyId': 'P973', 'Type': 'url'},
             {'Entity': 'Event', 'Column': 'Homepage', 'PropertyName': 'official website', 'PropertyId': 'P856', 'Type': 'url'},
             {'Entity': 'Event', 'Column': 'wikicfpId', 'PropertyName': 'WikiCFP event ID', 'PropertyId': 'P5124', 'Type': 'extid'},
             {'Entity': 'Event', 'Column': 'dblpId', 'PropertyName': 'DBLP event ID', 'PropertyId': 'P10692', 'Type': 'extid'},
             {'Entity': 'Proceedings', 'Column':None, 'PropertyName': 'instanceof', 'PropertyId': 'P31', 'Value': 'Q1143604'},
             {'Entity': 'Proceedings', 'Column': 'Acronym', 'PropertyName': 'short name', 'PropertyId': 'P1813', 'Type': 'text'},
             {'Entity': 'Proceedings', 'Column': 'Title', 'PropertyName': 'title', 'PropertyId': 'P1476', 'Type': 'text'},
             {'Entity': 'Proceedings', 'Column': 'OpenLibraryId', 'PropertyName': 'Open Library ID', 'PropertyId': 'P648', 'Type': 'extid'},
             {'Entity': 'Proceedings', 'Column': 'ppnId', 'PropertyName': 'K10plus PPN ID', 'PropertyId': 'P6721', 'Type': 'extid'},
             {'Entity': 'Proceedings', 'Column': 'Event', 'PropertyName': 'is proceedings from', 'PropertyId': 'P4745', 'Lookup': 'Q2020153'},
             {'Entity': 'Proceedings', 'Column': 'publishedIn', 'PropertyName': 'published in', 'PropertyId': 'P1433', 'Lookup': 'Q39725049'},
             {'Entity': 'Proceedings', 'Column': 'oclcId', 'PropertyName': 'OCLC work ID','PropertyId': 'P5331', 'Type': 'extid'},
             {'Entity': 'Proceedings', 'Column': 'isbn13', 'PropertyName': 'ISBN-13', 'PropertyId': 'P212', 'Type': 'extid'},
             {'Entity': 'Proceedings', 'Column': 'doi', 'PropertyName': 'DOI', 'PropertyId': 'P356', 'Type': 'extid'},
             {'Entity': 'Proceedings', 'Column': 'dblpId', 'PropertyName': 'DBLP event ID', 'PropertyId': 'P10692', 'Type': 'extid'},
             ]

        self.SmwMetadata = [
            *[{"Entity":"Event",
               "Column":r.get("templateParam"),
               "PropertyName":r.get("name"),
               "PropertyId":r.get("prop"),
               "TemplateParam": r.get("templateParam")
               } for r in OREvent.propertyLookupList
              ],
            *[{"Entity": "Event series",
               "Column": r.get("templateParam"),
               "PropertyName": r.get("name"),
               "PropertyId": r.get("prop"),
               "TemplateParam": r.get("templateParam")
               } for r in OREventSeries.propertyLookupList
              ]
        ]
