from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass()
class MonthRange:
    start: datetime
    end: datetime

    def get_filename(self):
        low_month_str = str(self.start.month).zfill(2)
        high_month_str = str(self.end.month).zfill(2)
        return f"{self.start.year}-{low_month_str} to {self.end.year}-{high_month_str}"

    def get_year_in_range(self, month: int):
        if self.start.year == self.end.year:
            return self.start.year

        # goes over an end of year
        if month >= self.start.month:
            return self.start.year
        return self.end.year

    def contains_date(self, date: datetime):
        return date >= self.start and date <= self.end


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

        month_following = datetime(high_year, high_month, 28) + timedelta(days=4)
        high_date = month_following.replace(day=1) - timedelta(days=1)

        return MonthRange(low_date, high_date)
    except:
        return None
