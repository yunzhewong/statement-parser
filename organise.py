from dataclasses import dataclass
from typing import Dict, List
from lib.Folder import Folder
from lib.MonthRange import MonthRange
from lib.dates import get_last_date_in_month
from lib.files import transactions_to_csv
from lib.json_config import get_json
from datetime import datetime

from lib.transaction import Transaction
from summarise import short_summary

OUTPUT_PATH = "data"


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
        return SingleMonthRange(month=new_month, year=year)


known_range_with_transactions = SingleMonthRange(month=3, year=2024)


def collate_transactions(folders: List[Folder], single_month_range: SingleMonthRange):
    month_range = single_month_range.to_month_range()

    transactions: List[Transaction] = []
    for folder in folders:
        transactions += folder.get_transactions_between_dates(month_range)

    sorted_transactions = sorted(transactions, key=lambda x: x.date)

    output_csv_name = f"{month_range.to_filename()}.csv"
    transactions_to_csv(OUTPUT_PATH, output_csv_name, sorted_transactions)

    short_summary(sorted_transactions)
    print()


if __name__ == "__main__":
    suffixes: dict = get_json("suffixes.json")

    folders = [Folder(path) for path in suffixes.values()]

    for year in range(start_year, current_date.year):
        for month in range(1, 13):
            collate_transactions(folders, month, year)

    for month in range(1, current_date.month):
        collate_transactions(folders, month, current_date.year)
