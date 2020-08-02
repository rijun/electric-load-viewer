import os
import pathlib
import sqlite3
from typing import List, Optional

import pandas as pd


class DataHandler:
    def __init__(self):
        """Class to retrieve and prepare the meter data for later use in the callbacks."""
        # Get meter data
        p = pathlib.Path(os.path.realpath(__file__)).parent
        self._db_path = p / '..' / 'itp.db'
        if not self._db_path.exists():
            print("Database file not found! Exiting...")
            exit(-1)
        con = sqlite3.connect(self._db_path)
        self._df = pd.read_sql_query("SELECT datum_zeit, obis_180 FROM zaehlwerte "
                                     "WHERE strftime('%M', datum_zeit) % 15 = 0;",
                                     con, parse_dates='datum_zeit')
        con.close()
        # Remove duplicate entries
        self._df = self._df.set_index('datum_zeit')
        self._df = self._df.loc[~self._df.index.duplicated(keep='first')]
        # Reindex to add missing dates
        idx = pd.date_range(self._df.index.min(), self._df.index.max(), freq='T')
        self._df = self._df.reindex(idx)
        # Interpolate if necessary and calculate meter diffs
        self._df = self._df.interpolate()
        self._df['diff'] = self._df['obis_180'].diff()
        self._df['date_time'] = self._df.index  # Required for aggregation

        self._overview_df = self._df.resample('D').agg({'obis_180': 'first', 'diff': 'sum'})

    def day(self, date: str) -> pd.DataFrame:
        """
        Return a DataFrame containing all entries of one day.

        :param date: The requested date
        """
        return self._df[date]

    def overview(self) -> pd.DataFrame:
        """Return a DataFrame with datetime as index and obis_180 and diff as columns, aggregated with first() and
        sum() respectively."""
        return self._overview_df

    def first_date(self) -> float:
        """Return the first date in the DataFrame."""
        return self._df.index.date.min()

    def last_date(self) -> float:
        """Return the last date in the DataFrame."""
        return self._df.index.date.max()

    def available_months(self) -> List[str]:
        """Return a list of formatted strings (YYYY-MM) with the months available in the database."""
        return [i for i in pd.Series(self._df.index.year.astype(str) + '-' + self._df.index.month.astype(str)).unique()]

    def available_years(self) -> List[str]:
        """Return a list of formatted strings (YYYY) with the years available in the database."""
        return [i for i in self._df.index.year.unique()]

    def min(self, start: Optional[str] = None, end: Optional[str] = None) -> float:
        """
        Return the minimum diff value for a given date range. If no parameters are passed, the first and last dates in
        the internal DataFrame will be used.

        :param start: The first date of the range (YYYY-MM-DD)
        :param end: The last date of the range (YYYY-MM-DD)
        """
        start = self.first_date() if start is None else start
        end = self.last_date() if end is None else end
        return round(float(self._overview_df[start:end]['diff'].min()), 2)

    def max(self, start: Optional[str] = None, end: Optional[str] = None) -> float:
        """
        Return the maximum diff value for a given date range.

        :param start: The first date of the range (YYYY-MM-DD)
        :param end: The last date of the range (YYYY-MM-DD)
        """
        start = self.first_date() if start is None else start
        end = self.last_date() if end is None else end
        return round(float(self._overview_df[start:end]['diff'].max()), 2)

    def mean(self, start: Optional[str] = None, end: Optional[str] = None) -> float:
        """
        Return the mean diff value for a given date range.

        :param start: The first date of the range (YYYY-MM-DD)
        :param end: The last date of the range (YYYY-MM-DD)
        """
        start = self.first_date() if start is None else start
        end = self.last_date() if end is None else end
        return round(float(self._overview_df[start:end]['diff'].mean()), 2)

    def sum(self, start: Optional[str] = None, end: Optional[str] = None) -> float:
        """
        Return the sum of all diff values for a given date range.

        :param start: The first date of the range (YYYY-MM-DD)
        :param end: The last date of the range (YYYY-MM-DD)
        """
        start = self.first_date() if start is None else start
        end = self.last_date() if end is None else end
        return round(float(self._overview_df[start:end]['diff'].sum()), 2)

    def yearly_energy_usage(self):
        """
        Calculate the previous yearly energy usage.

        If the number of days in the dataset is > 365 (one year), the sum of all meter values for the last 365 days is
        returned. Otherwise, the currently stored meter values are summed up and interpolated to the a duration of one
        year.
        """
        if self._df.index.size < 365:  # Dataset smaller than one year
            energy_used = self._df.sum(axis=1).div(4).sum()
            energy_used = energy_used / self._df.index.size * 365  # Scale to one year
        else:
            energy_used = self._df.iloc[-366:-1].sum(axis=1).div(4).sum()  # Calculate sum of last 365 values
        return round(energy_used / 1000, 2)  # Convert Wh to kWh
