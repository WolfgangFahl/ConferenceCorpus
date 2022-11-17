import numpy as np
import calendar
from datetime import datetime, timedelta, date
from typing import List, Union

from corpus.utils.plots import Plot


class DatePolarHistogram(Plot):
    """
    polar histogram for dates
    only month and date are plotted the year is ignored

    see https://matplotlib.org/2.0.2/jpexamples/pie_and_polar_charts/polar_bar_demo.html
    """

    bottom = 0

    def __init__(self, dates: List[Union[datetime, date]], title:str=None):
        """
        constructor

        Args:
            dates(list): list of dates the dates need to be a pared date object
            title(str): title of the plot
        """
        self.setup(title)
        hist={monthDay:0 for monthDay in self.__getBaseNumbers()}
        for date in dates:
            monthDay = self.getMonthDateNumber(date)
            if monthDay in hist:
                hist[monthDay] += 1
        data = np.array(list(hist.values()))
        N = len(hist)
        theta = np.linspace(0.0, 2 * np.pi, N, endpoint=False)
        radii = data
        width = (2*np.pi) / N
        self.ax = self.plt.subplot(polar=True)
        self.bars = self.ax.bar(theta, radii, width=width, bottom=self.bottom)
        positions, labels = self.__get_x_ticks()
        positions = [theta[i] for i in positions]
        self.plt.xticks(positions, labels)

    def __get_x_ticks(self) -> (List[int], List[str]):
        """
        Generates the ticks and labels for the x-axis

        Returns:
            (positions, labels) position and label of the ticks
        """
        position = []
        labels = []
        day = 0
        for i in range(1,13):
            position.append(day)
            labels.append(calendar.month_name[i])
            days_in_month = calendar.monthrange(2020, i)[1]
            day += days_in_month
        return position, labels

    @staticmethod
    def getMonthDateNumber(date: Union[datetime, date]) -> int:
        """
        Converts the given date into a number based on month and date
        Format: monthDate
        Example:
            2022-03-05 → 305
            2022-10-10 → 1010

        Args:
            date: date to convert

        Returns:
            int monthDate
        """
        day = date.day
        if day <10:
            day = f'0{day}'
        else:
            day = f"{day}"
        month = str(date.month)
        return int(f"{month}{day}")

    @staticmethod
    def gen_days_of_year(year: int) -> List[datetime]:
        """
        Generates a list of all dates within the given year
        see https://stackoverflow.com/questions/32507287/how-to-generate-range-of-dates-every-day-of-a-given-year
        Args:
            year: year for which all dates should be generated

        Returns:
            list of all dates in the given year
        """
        start_date=datetime( year, 1, 1 )
        end_date=datetime( year, 12, 31 )
        d=start_date
        dates=[ start_date ]
        while d < end_date:
            d += timedelta(days=1)
            dates.append( d )
        return dates

    def __getBaseNumbers(self) -> List[int]:
        """
        Returns:
             list of all possible numbers on the DatePolarHistogram spectrum
        """
        leapyear = 2020  # does not matter which
        return [DatePolarHistogram.getMonthDateNumber(date) for date in DatePolarHistogram.gen_days_of_year(leapyear)]