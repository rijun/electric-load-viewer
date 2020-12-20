import datetime
import os
import pathlib

import holidays
import pandas as pd


class DefaultLoadProfile:
    def __init__(self):
        """
        Class to calculate the default load profile of a given day for the household customer group.
        Uses the data of two .csv files as lookup tables for the load profile data, these files must be present.
        """
        parent = pathlib.Path(os.path.realpath(__file__)).parent
        self._static_lookup = pd.read_csv(parent / 'profile.csv', header=[0, 1], index_col=0).transpose()
        self._dynamic_lookup = pd.read_csv(parent / 'factors.csv').set_index('day_no')

    def calculate_profile(self, date: str, energy_usage: float = 1000, shift=False):
        """
        For a given date, calculate the default load profile with respect to the day type and season.

        :param date: Date for which the default load profile should be calculated
        :param energy_usage: Yearly energy usage in kWh, defaults to 1000 kWh if not specified.
        :param shift: Shift the index by 15 minutes to the left, e.g. 0:00-23:45 instead of 0:15-0:00
        :return: Pandas series with the default load profile values for the given day
        """
        date = datetime.date.fromisoformat(date)
        static_profile_values = self._static_profile_values(date, energy_usage)
        profile_values = static_profile_values.mul(self._dynamization_factor(date)).round(1)

        # Handle daylight saving times switch
        if date.month == 3 and date.day >= 25 and date.weekday() == 6:  # Check if date is the last sunday of march
            profile_values.loc['2:15':'3:00'] = 0

        # Adjust index if necessary
        if shift:
            idx = pd.date_range(date, date + datetime.timedelta(1), freq='15T')[:-1]
        else:
            idx = pd.date_range(date, date + datetime.timedelta(1), freq='15T')[1:]
        profile_values.index = idx

        return profile_values

    def _static_profile_values(self, date: datetime.date, energy_usage: float) -> pd.Series:
        """Returns the static profile values for the provided day."""
        values = self._static_lookup.loc[self._season_type(date), self._day_type(date)]
        values = values.mul(energy_usage / 1000)    # Account for normalization
        return values

    def _dynamization_factor(self, date: datetime.date) -> pd.Series:
        """Returns the dynamization factor for the provided day."""
        return self._dynamic_lookup.loc[date.timetuple().tm_yday]['value']

    @staticmethod
    def _day_type(d):
        """Returns the type of day according to the default load profile specifications."""
        if d in holidays.Germany() or d.isoweekday() == 7:
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
