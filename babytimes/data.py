"""tools for working with baby data
"""

from pydantic.dataclasses import dataclass
from functools import cached_property
import glob
import pandas as pd
from typing import List
import datetime as dt


@dataclass
class Times:
    loc: str

    @cached_property
    def df(self) -> pd.DataFrame:
        find_fp = glob.glob(f"{self.loc}/*.zip")
        assert len(find_fp) == 1
        return pd.read_csv(find_fp[0], skiprows=9)


@dataclass
class Sleeptimes:
    times: Times

    @property
    def fields(self) -> List[str]:
        return ["sec", "typ"] + [
            i for typ in ["begin", "end"] for i in [typ, f"{typ}_time", f"{typ}_date"]
        ]

    @cached_property
    def just_sleep(self) -> pd.DataFrame:
        return self.times.df[self.times.df.typeKey == "SLEEP"]

    def add_time_fields(self) -> None:
        self.just_sleep["begin"] = pd.to_datetime(self.just_sleep["beginDatetimeLocal"])
        self.just_sleep["end"] = pd.to_datetime(
            self.just_sleep["SLEEP_endDatetimeLocal"]
        )
        self.just_sleep["sec"] = self.just_sleep["SLEEP_durationSeconds"]
        for typ in ["begin", "end"]:
            self.just_sleep[f"{typ}_time"] = self.just_sleep[typ].dt.time
            self.just_sleep[f"{typ}_date"] = self.just_sleep[typ].dt.date

    def add_typ(self) -> None:
        def typ(row) -> str:
            if (
                row.begin_time >= dt.time(hour=19) or row.begin_time <= dt.time(hour=10)
            ) and row.end_time <= dt.time(hour=10):
                return "night"
            else:
                return "nap"

        self.just_sleep["typ"] = self.just_sleep.apply(typ, axis=1)

    @cached_property
    def df(self) -> pd.DataFrame:
        self.add_time_fields()
        self.add_typ()
        return self.just_sleep[self.fields]

    @cached_property
    def cross_dates(self) -> pd.DataFrame:
        rel = self.df[self.df.begin_date != self.df.end_date]

        def end_of_day(begin_dt: dt.datetime) -> dt.datetime:
            return dt.datetime(
                year=begin_dt.year,
                month=begin_dt.month,
                day=begin_dt.day,
                hour=23,
                minute=59,
                second=59,
            )

        def begin_of_day(end_dt: dt.datetime) -> dt.datetime:
            return dt.datetime(
                year=end_dt.year,
                month=end_dt.month,
                day=end_dt.day,
                hour=0,
                minute=0,
                second=0,
            )

        first_part = rel.assign(end=rel.begin.map(end_of_day))[["begin", "end"]]
        second_part = rel.assign(begin=rel.end.map(begin_of_day))[["begin", "end"]]
        return pd.concat([first_part, second_part])

    @cached_property
    def same_day(self) -> pd.DataFrame:
        rel = self.df[self.df.begin_date == self.df.end_date]
        return rel[["begin", "end"]]

    @cached_property
    def df_viz(self) -> pd.DataFrame:
        return pd.concat([self.same_day, self.cross_dates])