import datetime

import holidays
import pandas as pd


class DefaultLoadProfile:
    _holidays = holidays.Germany()

    def __init__(self):
        """
        A class to calculate the default load profile of a given day.
        """
        self._static_lookup = pd.read_csv('profile.csv', header=[0, 1], index_col=0).transpose()
        self._dynamic_lookup = pd.read_csv('dynamisierung.csv').set_index('day_no')

    def calculate_profile(self, date: str, energy_usage: float = 1000):
        """
        For a given date, calculate the default load profile with respect to the day type and season.

        :param date: Date for which the default load profile should be calculated
        :param energy_usage: Yearly energy usage in kWh, defaults to 1000 kWh if not specified.
        :return: Pandas series with the values from 0:15 to 0:00 the next day
        """
        date = datetime.date.fromisoformat(date)
        idx = pd.date_range(date, date + datetime.timedelta(1), freq='15T')[1:]
        ret_data = self._dynamic_profile_values(date, energy_usage)
        ret_data.index = idx
        return ret_data

    def _static_profile_values(self, date: datetime.date, energy_usage: float) -> pd.Series:
        """Calculate the static profile values for the provided day."""
        ret_values = self._static_lookup.loc[self._season_type(date), self._day_type(date)]
        ret_values = ret_values.mul(1E-3).mul(energy_usage / 1000)    # Scale values kW and to account for normalization
        return ret_values

    def _dynamic_profile_values(self, date: datetime.date, energy_usage: float) -> pd.Series:
        """Calculate the dynamic profile values for the provided day."""
        return self._static_profile_values(date, energy_usage)\
            .mul(self._dynamic_lookup.loc[date.timetuple().tm_yday]['value'])\
            .round(1)

    @classmethod
    def _day_type(cls, d):
        """Returns the type of day according to the default load profile specifications."""
        if d in cls._holidays or d.isoweekday() == 7:
            return "sunday"
        # Handle christmas eve
        elif d.month == 12 and d.day == 24 and d.weekday() != 6:
            return "saturday"
        # Handle new years eve
        elif d.month == 12 and d.day == 31 and d.weekday() != 6:
            return "saturday"
        elif d.isoweekday() == 6:
            return "saturday"
        else:
            return "weekday"

    @staticmethod
    def _season_type(d):
        """Returns the corresponding season according to the default load profile specifications."""
        if d < datetime.date(d.year, 3, 21):
            return "winter"
        elif d < datetime.date(d.year, 5, 15):
            return "transition"
        elif d < datetime.date(d.year, 9, 15):
            return "summer"
        elif d < datetime.date(d.year, 11, 1):
            return "transition"
        else:
            return "winter"
