import json
import math
import re
from statistics import median
from typing import List, Tuple

from fb4.widgets import LodTable
from flask import Blueprint, request, jsonify
from ortools.sat.python import cp_model
from num2words import num2words


class EventSeriesBlueprint():
    """
    API service for event series completion
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
        self.blueprint = Blueprint(name, __name__, template_folder=self.template_folder, url_prefix=f"/{name}")
        self.app = app
        self.appWrap = appWrap

        @self.blueprint.route('/<name>')
        def getEventSeries(name: str):
            return self.getEventSeries(name)

        @self.blueprint.route('/complete', methods=['POST'])
        @self.appWrap.csrf.exempt
        def completeSeries():
            return self.completeSeries()

        app.register_blueprint(self.blueprint)

    @property
    def debug(self):
        return self.appWrap.debug

    def getEventSeries(self, name:str):
        '''
        Query multiple datasources for the given event series

        Args:
            name(str): the name of the event series to be queried
        '''
        multiQuery="select * from {event}"
        variable = self.appWrap.lookup.getMultiQueryVariable(multiQuery)
        if self.debug:
            print(f"found '{variable}' as the variable in '{multiQuery}'")
        #self.lookup.load()
        idQuery = f"""select source,eventId from event where acronym like "%{name}%" order by year desc"""
        dictOfLod = self.appWrap.lookup.getDictOfLod4MultiQuery(multiQuery, idQuery)
        return self.appWrap.convertToRequestedFormat(dictOfLod)

    def completeSeries(self):
        """
        Completes sent event series and returns it

        Returns:
            dict of LoDs
        """
        dLoD = json.loads(request.data)
        if isinstance(dLoD, dict):
            for name, lod in dLoD.items():
                dLoD[name] = EventSeriesCompletion.completeSeries(lod)
        return jsonify(dLoD)


class EventSeriesCompletion(object):
    """
    Has different functionalities need to complete a event series
    """

    @staticmethod
    def getFrequency(lod:List[dict]) -> float:
        """
        Tries to extract the series frequency from the given set of events.
        Assumptions:
            - all events have the property year
            - at least two have the property ordinal
            - no event record is a duplicate

        Args:
            lod: list of event records

        Returns:
            float number of series per year
        """
        oys, steps=EventSeriesCompletion._getFrequencySteps(lod)
        # calc step size
        stepSizes=[ordinalStep/yearStep if yearStep > 0 else 0 for ordinalStep, yearStep in steps]
        # handle multiple events per year
        for i, stepSize in enumerate(stepSizes):
            if stepSize == 0:
                startIndex = max(0, i-1)
                countSameYear = max(1,int(stepSizes[startIndex]))
                countIndex=0
                for s in stepSizes[i:]:
                    if s == 0:
                        countSameYear += 1
                        countIndex+=1
                    else:
                        break
                for j in range(startIndex,i+countIndex):
                    stepSizes[j]=countSameYear
        res = []
        currentInverval=0
        for i, (ordinal, year) in enumerate(oys):
            if i == len(oys)-1 or stepSizes[currentInverval] != stepSizes[max(0,i-1)]:
                res.append({"start":oys[currentInverval][1], "end":year, "frequency":stepSizes[currentInverval]})
                currentInverval=i
        return res

    @staticmethod
    def _getFrequencySteps(lod:List[dict]) -> Tuple[List[tuple],List[tuple]]:
        """
        Generates a list of
        Args:
            lod:

        Returns:
            List of frequency steps
        """
        lod.sort(key=lambda r: r.get("year", -1))
        # list of (ordinal, year) tuples
        oys = [(int(r.get("ordinal")), int(r.get("year"))) for r in lod if "ordinal" in r]
        steps = []
        for i, (ordinal, year) in enumerate(oys[:-1]):
            nextStepOrdinal, nextStepYear = oys[i + 1]
            steps.append((nextStepOrdinal - ordinal, nextStepYear - year))
        return oys, steps

    @staticmethod
    def hasMissingEvents(lod:List[dict])->bool:
        """

        Args:
            lod: list of event records

        Returns:
            True if the series has missing events. Otherwise false
        """
        oys, steps=EventSeriesCompletion._getFrequencySteps(lod)
        return all(1 == ordinalStep for ordinalStep, yearStep in steps)

    @staticmethod
    def isFrequencyConsistent(lod:List[dict])->bool:
        """
        Checks if the frequency of the series is consistent and thus has no change in the frequency
        Frequency reduced to occurs every n years (inconsistent if multiple events per year)
        Args:
            lod: list of event records

        Returns:
            True if the series is frequency consistent. Otherwise False
        """
        lod = [d for d in lod if d.get("year", None) is not None and d.get("ordinal", None) is not None]
        lod.sort(key=lambda record: (int(record.get("year")), int(record.get("ordinal"))))
        if len(lod) > 1:
            maxOrdinalStep = int(lod[-1].get("ordinal")) - int(lod[0].get("ordinal"))
            maxYearStep = int(lod[-1].get("year")) - int(lod[0].get("year"))
            if maxYearStep<1 or maxOrdinalStep<1:
                return False
            frequency = maxYearStep / maxOrdinalStep
            if frequency >= 1 and frequency.is_integer():
                return True
            else:
                return False
        else:
            return True

    @staticmethod
    def isConsiderable(lod:List[dict])->bool:
        """
        Checks if the given set of event records has at least two pairs of ordinal and year values
        Args:
            lod: list of event records

        Returns:
            True if the series is considerable
        """
        lod = [d for d in lod if d.get("year", None) is not None and d.get("ordinal", None) is not None]
        lod.sort(key=lambda record: (int(record.get("year")), int(record.get("ordinal"))))
        return len(lod) > 1

    @staticmethod
    def addGhostEvents(lod:List[dict]) -> List[dict]:
        """
        Adds missing event records in form of ghost records which represent the missing event and contain basic
        information such as ordinal and year.
        Assumption:
            - event records have an ordinal and year (this function only adds missing event records)

        Args:
            lod: list of event records

        Returns:
            list of event records
        """
        # Currently only frequency consistent series are supported
        if not EventSeriesCompletion.isFrequencyConsistent(lod):
            print("Series is not frequency consistent and thus no ghost events could be added") # ToDo: add support
            # frequencies = EventSeriesCompletion.getFrequency(lod)
            # res = []
            # for frequencyInterval in frequencies:
            #     start = frequencyInterval.get("start")
            #     end = frequencyInterval.get("end")
            #     freq = frequencyInterval.get("frequency")
            #     recordsOfInterval = [d for d in lod if start <= int(d.get("year")) and int(d.get("year")) < end]
            #     completedRecordsOfInterval = EventSeriesCompletion.addGhostEvents(recordsOfInterval)
            #     res.extend(completedRecordsOfInterval)
            return lod
        frequencies = EventSeriesCompletion.getFrequency(lod)
        if not frequencies:
            return lod
        frequency = frequencies[0].get("frequency")
        lod.sort(key=lambda record: int(record.get("ordinal", -1)))

        completedRecords = []
        lastOrdinal = int(lod[-1].get("ordinal"))
        inception=int(lod[-1].get("year") - lastOrdinal / frequency)
        for ord in range(1,lastOrdinal+1):
            if int(lod[0].get("ordinal")) == ord:
                completedRecords.append(lod[0])
                del lod[0]
            else:
                record = {
                    "year": int(inception + math.ceil(ord*frequency)),
                    "ordinal": ord
                }
                completedRecords.append(record)
            if frequency <= 1:
                # workaround for handling duplicate events
                for record in lod:
                    if record.get("year") == int(inception + math.ceil(ord*frequency)):
                        completedRecords.append(lod[0])
                        del lod[0]
                    else:
                        break
        return completedRecords


    @staticmethod
    def completeSeries(lod:List[dict]) -> List[dict]:
        """
        Tries to extract and add the ordinal information of event records
        Assumption:
            - each record has the property year

        Args:
            lod: list of event records

        Returns:
            list of event records
        """
        # 1) guess the ordinal based on the title and separate the records without guessable ordinal
        needToBeReassigned = []
        data = []
        for record in lod:
            guessedOrdinal = EventSeriesCompletion.guessOrdinal(record)
            if record.get("ordinal", None):
                guessedOrdinal.append(int(record.get("ordinal")))
            if guessedOrdinal is None or len(guessedOrdinal) == 0:
                needToBeReassigned.append(record)
            else:
                data.append((record, guessedOrdinal))
        # 2) Check consistency
        ocRecords = EventSeriesCompletion.ordinalYearConstraintSatProgram(data)
        if ocRecords is None:
            print("series is not ordinal consistent")
            return lod
        # 3)  Assign ordinal if found
        events=[]
        for record, ordinal in ocRecords:
            if "ordinal" in record and int(record["ordinal"]) != ordinal:
                print(f"Found ordinal diverges from existing ordinal {ordinal} != {record['ordinal']} (found!=existing) - {record['title']}")
            record['ordinal'] = ordinal
            events.append(record)
        # 4) Add ghost events
        eventsCompleted = EventSeriesCompletion.addGhostEvents(events)
        # 5) try to reassign unmatched event records to ghost events
        if needToBeReassigned:
            for i, record in enumerate(eventsCompleted):
                if len(record)==2 and "ordinal" in record and "year" in record:
                    # ghost event
                    possibleMatches = list(filter(lambda event: int(event.get("year")) == record.get("year"), needToBeReassigned))
                    if len(possibleMatches)>1:
                        possibleMatches.sort(key=lambda event:event.get('startDate', 0))
                        eventsCompleted[i] = {**possibleMatches[0], **record}
                        needToBeReassigned.remove(possibleMatches[0])
        return eventsCompleted+needToBeReassigned


    @staticmethod
    def guessOrdinal(record: dict) -> list:
        """
        tries to guess the ordinal of the given record by returning a set of potential ordinals
        Assumption:
            - given record must have the property 'title'

        Args:
            record: event record

        Returns:
            list of potential ordinals
        """
        title = record.get('title', None)
        if title is None:
            return []
        ord_regex = r"(?P<ordinal>[0-9]+)(?: ?st|nd|rd|th)"
        potentialOrdinal=[]
        match = re.findall(pattern=ord_regex, string=title)
        potentialOrdinal.extend([int(ord) for ord in match])
        # search for ordninals in textform
        for lang in ['en']:
            for ord in range(1,100):
                ordWord = num2words(ord, lang=lang, to='ordinal')
                if ordWord in title.lower() or ordWord.replace("-", " ") in title.lower():
                    potentialOrdinal.append(ord)
        return list(set(potentialOrdinal))

    @staticmethod
    def isOrdinalConsistent(lod: List[dict]) -> bool:
        """
        Checks if the given lod is ordinal consistent.

        Args:
            record: list of event records of belonging to the same event

        Returns:
            True if given LoD is ordinal consistent
        """
        lod = [d for d in lod if d.get("year", None) is not None and d.get("ordinal", None) is not None]
        lod.sort(key=lambda record: (int(record.get("year")),int(record.get("ordinal"))))
        return all([int(lod[i].get("ordinal")) < int(lod[i+1].get("ordinal")) for i, r in enumerate(lod[:-1])])

    @staticmethod
    def isOrdinalStyleConsistent(lod: List[dict]) -> bool:
        """
        Checks if the given set of event records is ordinal style consistent
        Currently only distinguishes between ordinalText and ordinalNumber

        Args:
            lod: list of event records of belonging to the same event

        Returns:
            True if given LoD is ordinal style consistent
        """
        ordNum=0
        ordText=0
        for record in lod:
            title = record.get('title', None)
            if title is None:
                continue
            ord_regex = r"(?P<ordinal>[0-9]+)(?: ?st|nd|rd|th)"
            potentialOrdinal = []
            match = re.findall(pattern=ord_regex, string=title)
            if match:
                ordNum+=1
            # search for ordninals in textform
            for lang in ['en']:
                for ord in range(1, 100):
                    ordWord = num2words(ord, lang=lang, to='ordinal')
                    if ordWord in title.lower():
                        ordText+=1
        return ordNum==0 or ordText==0

    @staticmethod
    def ordinalYearConstraintSatProgram(data:list, debug:bool=False):
        """
        Checks if a ordinal assignment can be found which satisfies the ordinal consistency for the given event records.
        Args:
            data: list of tuples (event record, possible ordinals)
            debug: If true show debug messages

        Returns:
            list of tuples (event record, assigned ordinal), None of no solution was found
        """
        # Creates the model.
        model = cp_model.CpModel()
        vars=[]
        perYear={}
        for record, ords in data:
            x=model.NewIntVarFromDomain(cp_model.Domain.FromIntervals([[ord,ord] for ord in ords]),record.get('title'))
            vars.append((record,x))
            year=record.get("year")
            if year not in perYear:
                perYear[year]=[(record,x)]
            else:
                perYear[year].append((record,x))
        order=list(perYear.keys())
        order.sort()
        for i, year in enumerate(order):
            for record, x in perYear[year]:
                for record, y in perYear[year]:
                    model.Add(x <= y)
            if i != len(order)-1:
                for record, x in perYear[year]:
                    for record, y in perYear[order[i+1]]:
                        model.Add(x < y)

        # Creates a solver and solves the model.
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            if debug:
                for record, var in vars:
                    print(f'{var.Name()} = {solver.Value(var)}')
            res = [(record, solver.Value(var)) for record, var in vars]
            return res
        else:
            if debug:
                print('No solution found.')
            return None

