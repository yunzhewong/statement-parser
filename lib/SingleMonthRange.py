from dataclasses import dataclass
from datetime import datetime

from lib.MonthRange import MonthRange
from lib.dates import get_last_date_in_month


@dataclass
class SingleMonthRange:
    month: int
    year: int

    def to_month_range(self):
        start_date = datetime(self.year, self.month, 1)
        end_date = get_last_date_in_month(self.month, self.year)
        return MonthRange(start_date, end_date)

    def get_incremented_copy(self, increment: int):
        new_month = self.month + increment
        if new_month == 0:
            return SingleMonthRange(month=new_month + 12, year=self.year - 1)
        if new_month == 13:
            return SingleMonthRange(month=new_month - 12, year=self.year + 1)
        return SingleMonthRange(month=new_month, year=self.year)
