from datetime import datetime


class MonthRange:
    def __init__(self, start: datetime, end: datetime):
        self.start = start
        self.end = end

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
