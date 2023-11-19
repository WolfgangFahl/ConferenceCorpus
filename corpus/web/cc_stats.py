"""
Created on 2022-05-15

@author: wf
"""
from io import BytesIO
import base64
import pprint
import matplotlib as plt
from corpus.event import EventStorage
from corpus.utils.plots import Histogramm
from lodstorage.query import Query, QuerySyntaxHighlight
from lodstorage.lod import LOD
from ngwidgets.lod_grid import ListOfDictsGrid
from nicegui import ui


class Queries:
    """
    pre defined queries
    """

    def __init__(self):
        self.queries = [
            {
                "name": "OrdinalHistogramm",
                "query": """SELECT ordinal
    FROM %s
    where ordinal is not null
    and ordinal < %s
    """,
            }
        ]
        self.queriesByName, _dup = LOD.getLookup(self.queries, "name")

    def getQuery(self, name, tableName, param):
        rawQuery = self.queriesByName[name]
        sqlQuery = rawQuery["query"] % (tableName, param)
        return sqlQuery


class Dashboard:
    """
    statistics dashboard for the conference corpus
    """

    def __init__(self, webserver, debug: bool = False):
        self.webserver = webserver
        self.debug = debug
        self.sqlDB = EventStorage.getSqlDB()
        self.eventViewTables = EventStorage.getViewTableList("event")
        self.setTableName(self.eventViewTables[0]["name"])
        self.columnName = "source"
        self.queries = Queries()
        self.queryName = "OrdinalHistogramm"
        self.maxValue = 50
        plt.use("WebAgg")
        try:
            self.setup_stats_page()
        except Exception as ex:
            self.webserver.handle_exception(ex)

    def setup_stats_page(self):
        """
        setup the ConferenceCorpus statistics page
        """
        self.histoGrammButton = ui.button(
            "histogramm", icon="bar_chart_4_bars", on_click=self.onHistogramm
        )
        self.queryButton = ui.button(
            "query", icon="question_mark", on_click=self.onQueryClick
        )

        self.resultDiv = ui.html("result")
        self.lod_chartDiv = ui.html("chart")
        self.queryDiv = ui.html("query")

        self.tableSelect = ui.select(
            label="Table",
            options=[table["name"] for table in self.eventViewTables],
            on_change=self.onChangeTable,
            value=self.tableName,
        )

        self.columnSelect = ui.select(
            label="Column",
            options=self.columns,
            on_change=self.onChangeColumn,
            value=self.columnName,
        )

        self.querySelect = ui.select(
            label="Query",
            options=list(self.queries.queriesByName.keys()),
            on_change=self.onChangeQuery,
            value=self.queryName,
        )

        ui.label("Max Value")
        self.maxValueSlider = ui.slider(
            min=10, max=250, value=self.maxValue, on_change=self.onChangeMaxValue
        )

        self.updateColumnOptions()
        self.agGrid = ListOfDictsGrid()

    def lod_chart(self, title:str, lod, attr="count"):
        """
        Create a chart from the given list of dicts.
        """
        data = [record[attr] for record in lod]
        histogram = Histogramm(data)

        # Get the histogram image as a BytesIO object
        histogram_image_stream = histogram.get_image(
            xLabel=attr,
            yLabel="Frequency",
            title=title,
            alpha=0.75,
            density=True,
        )
    
        # Convert the image for NiceGUI
        image_base64 = base64.b64encode(histogram_image_stream.getvalue()).decode("utf-8")
        image_data = f"data:image/png;base64,{image_base64}"
        # Display the image in NiceGUI
        with self.lod_chartDiv:
            # see https://nicegui.io/documentation/image
            self.chart_image = ui.image(image_data).style("width: 500px; height: 300px;")

    def onChangeTable(self, msg: dict):
        """
        handle selection of a different table

        Args:
            msg(dict): the justpy message
        """
        if self.debug:
            print(msg)
        self.setTableName(msg.value)
        self.updateColumnOptions()

    def onChangeColumn(self, msg: dict):
        """
        handle change of column selection

        """
        self.columnName = msg.value

    def queryHighlight(self, name, sqlQuery):
        query = Query(name=name, query=sqlQuery, lang="sql")
        qs = QuerySyntaxHighlight(query)
        html = qs.highlight()
        return html

    def getTotals(self, tableName, columnName=None, withSyntax: bool = False):
        totalSql = f"""SELECT  COUNT(*) as total 
        FROM {tableName}
        """
        if columnName is not None:
            totalSql += f"WHERE {columnName} is not NULL"
        totalRows = self.sqlDB.query(totalSql)
        total = totalRows[0]["total"]
        html = None
        if withSyntax:
            html = self.queryHighlight(
                name=f"total for {tableName},{columnName}", sqlQuery=totalSql
            )
        if columnName is not None:
            result = {"table": tableName, "column": columnName, "count": total}
        else:
            result = {"table": tableName, "total": total}
        return result, html

    def reloadAgGrid(self, lod: list, showLimit=10):
        self.agGrid.load_lod(lod)
        if self.debug:
            pprint.pprint(lod[:showLimit])
        self.agGrid.options.columnDefs[0].checkboxSelection = True

    def onHistogramm(self, _msg):
        """
        handle a click of the histogramm button
        """
        try:
            totals = []
            self.queryDiv.inner_html = ""
            for eventView in self.eventViewTables:
                tableName = eventView["name"]
                try:
                    tableTotals, html = self.getTotals(tableName)
                    total = tableTotals["total"]
                    columnTotal, html = self.getTotals(
                        tableName, self.columnName, withSyntax=True
                    )
                    self.queryDiv.inner_html += html
                    columnTotal["total"] = total
                    columnTotal["percent"] = columnTotal["count"] / total * 100
                    totals.append(columnTotal)
                except Exception as totalFail:
                    self.webserver.handle_exception(totalFail)
            self.reloadAgGrid(totals)
        except Exception as ex:
            self.webserver.handle_exception(ex)

    def onQueryClick(self, _msg):
        """
        handle a click of the query button
        """
        try:
            sqlQuery = self.queries.getQuery(
                self.queryName, self.tableName, self.maxValue
            )
            html = self.queryHighlight(self.queryName, sqlQuery)
            self.queryDiv.content = html
            queryLod = self.sqlDB.query(sqlQuery)
            # self.reloadAgGrid(queryLod)
            self.lod_chart(
                lod=queryLod, attr="ordinal", title=f"{self.queryName} {self.tableName}"
            )
        except Exception as ex:
            self.webserver.handle_exception(ex)

    def onChangeQuery(self, msg):
        self.queryName = msg.value

    def onChangeMaxValue(self, msg):
        self.maxValue = msg.value

    def setTableName(self, tableName: str):
        """

        Args:
            tableName(str): the table name
        """
        self.tableName = tableName
        tableDict = self.sqlDB.getTableDict()
        self.columns = list(tableDict[tableName]["columns"])

    def updateColumnOptions(self):
        """
        Update the column select options based on the current table.
        """
        # Update the options of the columnSelect
        self.columnSelect.options = self.columns
        # Optionally, reset the value if the previous value is not in the new options
        if self.columnName not in self.columns:
            self.columnSelect.value = self.columns[0] if self.columns else None
