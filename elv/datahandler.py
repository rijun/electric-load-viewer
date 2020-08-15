import os
import pathlib
import sqlite3
from typing import List, Optional

import numpy as np
import pandas as pd

from elv.app import cache


class DataHandler:
    def __init__(self):
        """Class to retrieve and prepare the meter data for later use in the callbacks."""
        # Get meter data
        p = pathlib.Path(os.path.realpath(__file__)).parent
        self._db_path = p / '..' / 'itp.db'
        if not self._db_path.exists():
            print("Database file not found! Exiting...")
            exit(-1)
        self._cache_conn = sqlite3.connect(':memory:')
        self._cache_conn.execute("CREATE TABLE cache (date_time TEXT, session_id TEXT, data BLOB)")

    @cache.memoize()
    def _get_dataframe(self, session_id: str, meter_id: str):
        con = sqlite3.connect(self._db_path)
        df = pd.read_sql_query("SELECT datum_zeit, obis_180 FROM zaehlwerte WHERE strftime('%M', datum_zeit) % 15 = 0 "
                               "AND zaehler_id = (?);", con, params=[meter_id], parse_dates='datum_zeit')
        con.close()
        # Remove duplicate entries
        df = df.set_index('datum_zeit')
        df = df.loc[~df.index.duplicated(keep='first')]
        # Reindex to add missing dates
        idx = pd.date_range(df.index.min(), df.index.max(), freq='15T')
        df = df.reindex(idx)
        # Interpolate if necessary and calculate meter diffs
        df['interpolation'] = df['obis_180'].isna()
        df = df.interpolate()
        df['diff'] = df['obis_180'].diff()
        # df['diff_inter'] = df['diff'].loc[df['interpolation'] == True]
        # df.loc[(df['interpolation'] == True), 'diff'] = np.NaN
        # df.loc[(df['interpolation'] == False), 'diff_inter'] = 0
        # df.drop('interpolation', axis=1, inplace=True)
        df['date_time'] = df.index  # Required for aggregation
        return df

    def meters_in_database(self) -> list:
        """Return a list of all meter ids in the database."""
        con = sqlite3.connect(self._db_path)
        meters = [x[0] for x in con.execute("SELECT zaehler_id FROM zaehlpunkte;").fetchall()]
        con.close()
        return meters

    def meter_info(self, meter_id: str) -> tuple:
        """Query the meter information from the database."""
        con = sqlite3.connect(self._db_path)
        meter_info = con.execute("SELECT kunde_name, kunde_vorname, plz, ort FROM zaehlpunkte "
                                 "WHERE zaehler_id = (?);", [meter_id]).fetchall()[0]
        con.close()
        return meter_info

    def day(self, session_id: str, meter_id: str, date: str) -> pd.DataFrame:
        """Return a DataFrame containing all entries of one day."""
        return self._get_dataframe(session_id, meter_id)[date]

    def overview(self, session_id: str, meter_id: str) -> pd.DataFrame:
        """Return a DataFrame with datetime as index and obis_180 and diff as columns, aggregated with first() and
        sum() respectively."""
        return self._get_dataframe(session_id, meter_id).resample('D')\
            .agg({'obis_180': 'first', 'diff': 'sum', 'interpolation': 'first'})
            # .agg({'obis_180': 'first', 'diff': 'sum', 'interpolation': 'first'})

    def first_date(self, session_id: str, meter_id: str) -> float:
        """Return the first date in the DataFrame."""
        return self._get_dataframe(session_id, meter_id).index.date.min()

    def last_date(self, session_id: str, meter_id: str) -> float:
        """Return the last date in the DataFrame."""
        return self._get_dataframe(session_id, meter_id).index.date.max()

    def available_months(self, session_id: str, meter_id: str) -> List[str]:
        """Return a list of formatted strings (YYYY-MM) with the months available in the database."""
        return [i for i in pd.Series(
            self._get_dataframe(session_id, meter_id).index.year.astype(str) + '-' + self._get_dataframe(session_id,
                                                                                                         meter_id).index.month.astype(
                str)).unique()]

    def available_years(self, session_id: str, meter_id: str) -> List[str]:
        """Return a list of formatted strings (YYYY) with the years available in the database."""
        return [i for i in self._get_dataframe(session_id, meter_id).index.year.unique()]

    def min(self, session_id: str, meter_id: str, start: Optional[str] = None, end: Optional[str] = None) -> float:
        """
        Return the minimum diff value for a given date range. If no parameters are passed, the first and last dates in
        the internal DataFrame will be used.

        :param meter_id:
        :param session_id: The session id belonging to the request
        :param start: The first date of the range (YYYY-MM-DD)
        :param end: The last date of the range (YYYY-MM-DD)
        """
        start = self.first_date(session_id, meter_id) if start is None else start
        end = self.last_date(session_id, meter_id) if end is None else end
        return round(float(self.overview(session_id, meter_id)[start:end]['diff'].min()), 2)

    def max(self, session_id: str, meter_id: str, start: Optional[str] = None, end: Optional[str] = None) -> float:
        """
        Return the maximum diff value for a given date range.

        :param meter_id:
        :param session_id: The session id belonging to the request
        :param start: The first date of the range (YYYY-MM-DD)
        :param end: The last date of the range (YYYY-MM-DD)
        """
        start = self.first_date(session_id, meter_id) if start is None else start
        end = self.last_date(session_id, meter_id) if end is None else end
        return round(float(self.overview(session_id, meter_id)[start:end]['diff'].max()), 2)

    def mean(self, session_id: str, meter_id: str, start: Optional[str] = None, end: Optional[str] = None) -> float:
        """
        Return the mean diff value for a given date range.

        :param meter_id:
        :param session_id: The session id belonging to the request
        :param start: The first date of the range (YYYY-MM-DD)
        :param end: The last date of the range (YYYY-MM-DD)
        """
        start = self.first_date(session_id, meter_id) if start is None else start
        end = self.last_date(session_id, meter_id) if end is None else end
        return round(float(self.overview(session_id, meter_id)[start:end]['diff'].mean()), 2)

    def sum(self, session_id: str, meter_id: str, start: Optional[str] = None, end: Optional[str] = None) -> float:
        """
        Return the sum of all diff values for a given date range.

        :param meter_id:
        :param session_id: The session id belonging to the request
        :param start: The first date of the range (YYYY-MM-DD)
        :param end: The last date of the range (YYYY-MM-DD)
        """
        start = self.first_date(session_id, meter_id) if start is None else start
        end = self.last_date(session_id, meter_id) if end is None else end
        return round(float(self.overview(session_id, meter_id)[start:end]['diff'].sum()), 2)

    def yearly_energy_usage(self, session_id: str, meter_id: str):
        """
        Calculate the previous yearly energy usage.

        If the number of days in the dataset is > 365 (one year), the sum of all meter values for the last 365 days is
        returned. Otherwise, the currently stored meter values are summed up and interpolated to the a duration of one
        year.
        """
        if self._get_dataframe(session_id, meter_id).index.size < 365:  # Dataset smaller than one year
            energy_used = self._get_dataframe(session_id, meter_id).sum(axis=1).div(4).sum()
            energy_used = energy_used / self._get_dataframe(session_id, meter_id).index.size * 365  # Scale to one year
        else:
            energy_used = self._get_dataframe(session_id, meter_id).iloc[-366:-1].sum(axis=1).div(
                4).sum()  # Calculate sum of last 365 values
        return round(energy_used / 1000, 2)  # Convert Wh to kWh
