from dataclasses import dataclass
from datetime import datetime

from lib.dates import format_date, get_last_date_in_month


def year_month_to_string(year: int, month: int):
    return f"{year}-{str(month).zfill(2)}"


@dataclass()
class MonthRange:
    start: datetime
    end: datetime

    def to_filename(self):
        low = year_month_to_string(self.start.year, self.start.month)
        high = year_month_to_string(self.end.year, self.end.month)
        return f"{low} to {high}"

    def get_year_in_range(self, month: int):
        if self.start.year == self.end.year:
            return self.start.year

        # goes over an end of year
        if month >= self.start.month:
            return self.start.year
        return self.end.year

    def contains_date(self, date: datetime):
        return date >= self.start and date <= self.end


def parse_dashed_month_range(dashed_month_range: str):
    separated = dashed_month_range.split(" ")

    if len(separated) != 7:
        raise Exception("Expected 7 Elements")

    start = format_date(separated[1], separated[2])
    end = format_date(separated[5], separated[6])

    return MonthRange(start, end)


def get_month_range_from_filename(filename: str):
    last_dot = len(filename) - 1 - filename[::-1].find(".")
    name = filename[:last_dot]
    if len(name) != 18:
        return None

    try:
        low_year = int(name[0:4])
        low_month = int(name[5:7])

        low_date = datetime(low_year, low_month, 1)

        if name[8:10] != "to":
            return None

        high_year = int(name[11:15])
        high_month = int(name[16:18])

        high_date = get_last_date_in_month(high_month, high_year)

        return MonthRange(low_date, high_date)
    except:
        return None


def dates_overlap(range1: MonthRange, range2: MonthRange):
    return range1.start <= range2.end and range2.start <= range1.end
