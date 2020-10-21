import os
import pathlib
import sqlite3
from typing import List, Optional

import pandas as pd
import arrow


class DataHandler:
    def __init__(self):
        """Class to retrieve and prepare the meter data for later use in the callbacks."""
        database_filename = "itp.db"
        if os.environ.get('DOCKER_CONTAINER', False):
            self._db_path = pathlib.Path('/app') / database_filename
        else:
            p = pathlib.Path(os.path.realpath(__file__)).parent
            self._db_path = p / '..' / database_filename
        if not self._db_path.exists():
            raise ValueError("Database file not found.")

    def meters_in_database(self) -> list:
        """Return a list of all meter ids in the database."""
        con = sqlite3.connect(self._db_path)
        meters = [x[0] for x in con.execute("SELECT zaehler_id FROM zaehlpunkte;").fetchall()]
        con.close()
        return meters

    def meter_info(self, meter_id: str) -> tuple:
        """Query the meter information from the database."""
        con = sqlite3.connect(self._db_path)
        meter_info = con.execute("SELECT kunde_name, kunde_vorname, plz, ort FROM zaehlpunkte WHERE zaehler_id = (?);",
                                 [meter_id]).fetchall()[0]
        con.close()
        return meter_info

    def day(self, meter_id: str, date: str) -> pd.DataFrame:
        """Return a DataFrame containing all entries of one day."""
        next_day = arrow.get(date).shift(days=1).strftime("%Y-%m-%d")
        con = sqlite3.connect(self._db_path)
        df = pd.read_sql_query("SELECT datum_zeit, obis_180 FROM zaehlwerte WHERE datum_zeit BETWEEN (?) AND (?) "
                               "AND zaehler_id = (?);", con, params=[f"{date} 00:00", f"{next_day} 00:01", meter_id],
                               parse_dates='datum_zeit')
        con.close()
        return self._prepare_dataframe(df, '15T')

    def overview(self, meter_id: str, start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
        """Return a DataFrame with datetime as index and obis_180 and diff as columns, aggregated with first() and
        sum() respectively."""
        con = sqlite3.connect(self._db_path)
        df = pd.read_sql_query("SELECT datum_zeit, obis_180 FROM zaehlwerte WHERE time(datum_zeit) = '00:00:00' "
                               "AND zaehler_id = (?);", con, params=[meter_id], parse_dates='datum_zeit')
        df = self._prepare_dataframe(df, 'D')
        con.close()
        if start is not None and end is not None:
            return df.loc[start:end]
        else:
            return df

    def first_date(self, meter_id: str) -> str:
        """Return the first date in the DataFrame."""
        conn = sqlite3.connect(self._db_path)
        res = conn.execute("SELECT date(min(datum_zeit)) FROM zaehlwerte WHERE zaehler_id = (?)", [meter_id]).fetchone()
        conn.close()
        return res[0]

    def last_date(self, meter_id: str) -> str:
        """Return the last date in the DataFrame."""
        conn = sqlite3.connect(self._db_path)
        res = conn.execute("SELECT date(max(datum_zeit)) FROM zaehlwerte WHERE zaehler_id = (?)", [meter_id]).fetchone()
        conn.close()
        return res[0]

    def available_months(self, meter_id: str) -> List[str]:
        """Return a list of formatted strings (YYYY-MM) with the months available in the database."""
        conn = sqlite3.connect(self._db_path)
        res = conn.execute("SELECT strftime('%Y-%m', datum_zeit) AS year_month FROM zaehlwerte WHERE zaehler_id = (?) "
                           "GROUP BY year_month", [meter_id]).fetchall()
        conn.close()
        return [r[0] for r in res]

    def available_years(self, meter_id: str) -> List[str]:
        """Return a list of formatted strings (YYYY) with the years available in the database."""
        conn = sqlite3.connect(self._db_path)
        res = conn.execute("SELECT strftime('%Y', datum_zeit) AS year_month FROM zaehlwerte WHERE zaehler_id = (?) "
                           "GROUP BY year_month", [meter_id]).fetchall()
        conn.close()
        return [r[0] for r in res]

    def min(self, meter_id: str, start: Optional[str] = None, end: Optional[str] = None) -> float:
        """
        Return the minimum diff value for a given date range. If no parameters are passed, the first and last dates in
        the database are returned.

        :param meter_id:
        :param start: The first date of the range (YYYY-MM-DD)
        :param end: The last date of the range (YYYY-MM-DD)
        """
        start = self.first_date(meter_id) if start is None else start
        end = self.last_date(meter_id) if end is None else end
        return round(float(self.overview(meter_id)[start:end]['diff'].min()), 2)

    def max(self, meter_id: str, start: Optional[str] = None, end: Optional[str] = None) -> float:
        """
        Return the maximum diff value for a given date range.

        :param meter_id:
        :param start: The first date of the range (YYYY-MM-DD)
        :param end: The last date of the range (YYYY-MM-DD)
        """
        start = self.first_date(meter_id) if start is None else start
        end = self.last_date(meter_id) if end is None else end
        return round(float(self.overview(meter_id)[start:end]['diff'].max()), 2)

    def mean(self, meter_id: str, start: Optional[str] = None, end: Optional[str] = None) -> float:
        """
        Return the mean diff value for a given date range.

        :param meter_id:
        :param start: The first date of the range (YYYY-MM-DD)
        :param end: The last date of the range (YYYY-MM-DD)
        """
        start = self.first_date(meter_id) if start is None else start
        end = self.last_date(meter_id) if end is None else end
        return round(float(self.overview(meter_id)[start:end]['diff'].mean()), 2)

    def sum(self, meter_id: str, start: Optional[str] = None, end: Optional[str] = None) -> float:
        """
        Return the sum of all diff values for a given date range.

        :param meter_id:
        :param start: The first date of the range (YYYY-MM-DD)
        :param end: The last date of the range (YYYY-MM-DD)
        """
        start = self.first_date(meter_id) if start is None else start
        end = self.last_date(meter_id) if end is None else end
        return round(float(self.overview(meter_id)[start:end]['diff'].sum()), 2)

    @staticmethod
    def _prepare_dataframe(df: pd.DataFrame, frequency: str) -> pd.DataFrame:
        """
        Return a DataFrame with each quarter hour value (:15, :30, :45, :00) in the the database for the requested
        meter.

        :return: DataFrame with all values
        """
        # Remove duplicate entries
        df = df.set_index('datum_zeit')
        df = df.loc[~df.index.duplicated(keep='first')]
        # Reindex to add missing dates
        idx = pd.date_range(df.index.min(), df.index.max(), freq=frequency)
        df = df.reindex(idx)
        # Interpolate if necessary and calculate meter diffs
        df['interpolation'] = df['obis_180'].isna()
        df = df.interpolate()
        df['diff'] = df['obis_180'].diff().shift(-1)
        df.drop(df.tail(1).index, inplace=True)
        df['date_time'] = df.index  # Required for aggregation
        return df
