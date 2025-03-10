from typing import Dict, List
from lib.Folder import Folder
from lib.MonthRange import MonthRange
from lib.dates import get_last_date_in_month
from lib.files import export_to_csv
from lib.json_config import get_json
from datetime import datetime

from lib.transaction import Transaction
from summarise import short_summary

OUTPUT_PATH = "data"

start_year = 2023


def collate_transactions(folders: List[Folder], month: int, year: int):
    start_date = datetime(year, month, 1)
    end_date = get_last_date_in_month(month, year)
    query_range = MonthRange(start_date, end_date)

    transactions = []
    for folder in folders:
        transactions += folder.get_transactions_between_dates(query_range)

    def sort_key(x: Transaction):
        return x.date

    sorted_transactions = sorted(transactions, key=sort_key)

    export_to_csv(OUTPUT_PATH, query_range.get_filename() + ".csv", sorted_transactions)
    short_summary(sorted_transactions)
    print()


if __name__ == "__main__":
    suffixes: dict = get_json("suffixes.json")

    folders = [Folder(path) for path in suffixes.values()]

    current_date = datetime.now()

    for year in range(start_year, current_date.year):
        for month in range(1, 13):
            collate_transactions(folders, month, year)

    for month in range(1, current_date.month):
        collate_transactions(folders, month, current_date.year)
