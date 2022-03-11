'''
Created on 2022-04-03

@author: wf
'''
import re
import datetime

class Textparse(object):
    '''
    Basic Natural Language Processing on Text
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
    @staticmethod
    def strToDate(dateStr,dateFormat="%d.%m.%Y",debug:bool=False):
        '''
        convert the given string to a date
        
        Args:
            dateStr(str): the date string to convert
            dateFormat(str): the format to use for conversion
            debug(bool): if True show debug information
            
        Return:
            Date: - the converted data but None if there is a ValueError on conversion
        '''
        result=None
        try:
            result=datetime.datetime.strptime(
                        dateStr, dateFormat).date()
        except ValueError as ve:
            # TODO year might be ok but not garbage such as
            if debug:
                print(f"{dateStr}:{str(ve)}")
            pass
        return result
    
    @staticmethod
    def setDateRange(event,dateRange):
        for field in ["year","startDate","endDate"]:
            if field in dateRange:
                setattr(event,field,dateRange[field])
                
    @staticmethod
    def getDateRange(date):
        '''
        given a GND date string create a date range
        
        Args:
            date(str): the date string to analyze
            
        Returns:
            dict: containing year, startDate, endDate
        examples:
        2018-2019
        08.01.2019-11.01.2019
        2019
        1996.05.23-25
        2021.02.28-03.02
        '''
        result={}
        if date is not None:
            startDate=None
            endDate=None
            yearPattern="[12][0-9]{3}"
            monthPattern="01|02|03|04|05|06|07|08|09|10|11|12"
            dayPattern="01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31"
            datePattern="[0-9]{2}[.][0-9]{2}[.]"+yearPattern
            yearOnly=re.search(r"^("+yearPattern+")[-]?("+yearPattern+")?$",date)
            if yearOnly:
                result['year']=int(yearOnly.group(1))
            else:
                fromOnly=re.search(r"^("+datePattern+")[-]?$",date)
                if fromOnly:
                    startDate=Textparse.strToDate(fromOnly.group(1))
                else:
                    fromTo=re.search(r"^("+datePattern+")[-]("+datePattern+")$",date)
                    if fromTo:
                        startDate=Textparse.strToDate(fromTo.group(1))
                        endDate=Textparse.strToDate(fromTo.group(2))
                    else:
                        fromToSimple=re.search(r"^(?P<year>"+yearPattern+")\.(?P<month>"+monthPattern+")\.(?P<fromday>"+dayPattern+")[-]"+
                                               "((?P<untilmonth>"+monthPattern+")\.(?P<untildayWithMonth>"+dayPattern+")|(?P<untilday>"+dayPattern+"))$",date)
                        if fromToSimple:
                            year=fromToSimple.group("year")
                            month=fromToSimple.group("month")
                            untilmonth=fromToSimple.group("untilmonth")
                            if untilmonth is None:
                                untilmonth=month
                                untilday=fromToSimple.group("untilday")
                            else:
                                untilday=fromToSimple.group("untildayWithMonth")
                            fromday=fromToSimple.group("fromday")
                            dateFormat="%Y-%m-%d"
                            startDate=Textparse.strToDate(f"{year}-{month}-{fromday}",dateFormat=dateFormat)
                            endDate=Textparse.strToDate(f"{year}-{untilmonth}-{untilday}",dateFormat=dateFormat)
                            pass
            if startDate:
                result['startDate']=startDate
            if endDate:
                result['endDate']=endDate
        if 'startDate' in result:
                result['year']=result['startDate'].year
        return result

        