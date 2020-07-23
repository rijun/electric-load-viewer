import datetime

import holidays
import numpy as np
import pandas as pd

from elv import datahandler


class DefaultLoadProfile:
    _holidays = holidays.Germany()

    def __init__(self, data_handler: datahandler.DataHandler):
        self._df = None
        self._dh = data_handler

    def calculate_profile(self, date: str):
        if self._df is None:
            self._generate_profile()

        ret = self._df.loc[date]
        ret.index = pd.date_range(start=date, periods=len(ret), freq='15T')
        return ret

    def _generate_profile(self):
        # Generate DataFrame with required dates
        idx = pd.date_range(self._dh.first_date(), self._dh.last_date(), freq='D')
        df = pd.DataFrame(index=idx)
        df['day_of_year'] = df.index.dayofyear
        df['day_of_week'] = df.index.dayofweek
        # Mark each date according to day type and season
        df['day_type'] = df.index.to_series().apply(self._day_type)
        df['season_type'] = df.index.to_series().apply(self._season_type)
        # Create static load profile
        profil = pd.read_csv('profile.csv', header=[0, 1], index_col=0)
        df = pd.merge(df, profil.transpose(), how='left', left_on=['season_type', 'day_type'], right_index=True,
                      suffixes=('', '_y'))
        df.drop(df.filter(regex='_y$').columns.tolist(), axis=1, inplace=True)
        # Calculate energy used in one year
        if df.index.size < 365: # Dataset smaller than one year
            energy_used = df.sum(axis=1).div(4).sum()
            energy_used = energy_used / df.index.size * 365  # Scale to one year
        else:
            energy_used = df.iloc[-366:-1].sum(axis=1).div(4).sum()  # Calculate sum of last 365 values
        # Create dynamic values out of static values
        dynamics = pd.read_csv('dynamisierung.csv')
        dynamics = dynamics.set_index('day_no')
        col_list = df.columns[4:]
        row_list = []
        for row in df.itertuples(index=False):
            arr = np.array(list(row)[4:])
            row_list.append(np.round_(arr * dynamics.loc[row[0]]['value'], 1))
        df_dyn = pd.DataFrame(row_list)
        df_dyn.columns = col_list
        df_dyn.head()
        # Replace static values in DataFrame with dynamic ones
        df = df.drop(columns=df.columns[4:])
        df = pd.concat([df.reset_index(), df_dyn], axis=1).set_index('index')
        # Clean generated DataFrame
        df.index.name = ""
        df = df.drop(['day_of_year', 'day_of_week', 'day_type', 'season_type'], axis=1)
        # Convert values to kWh and scale to fit normalized values
        print(energy_used)
        df = df.mul(energy_used / 1000000).div(1000)
        self._df = df

    @classmethod
    def _day_type(cls, d):
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
        if d < datetime.datetime(d.year, 3, 21):
            return "winter"
        elif d < datetime.datetime(d.year, 5, 15):
            return "transition"
        elif d < datetime.datetime(d.year, 9, 15):
            return "summer"
        elif d < datetime.datetime(d.year, 11, 1):
            return "transition"
        else:
            return "winter"
