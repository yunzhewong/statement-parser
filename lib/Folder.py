from datetime import datetime
import os
from typing import List, Tuple

from lib.MonthRange import MonthRange, dates_overlap, get_month_range_from_filename
from lib.files import get_filenames
from lib.transaction import Transaction, get_transactions_in_csv


def get_filenames_between_dates(query_range: MonthRange, filenames: str):
    valid_month_ranges: List[str] = []
    for filename in filenames:
        month_range = get_month_range_from_filename(filename)
        if month_range is None:
            print(filename)
            continue

        if not dates_overlap(query_range, month_range):
            continue

        valid_month_ranges.append(filename)
    return valid_month_ranges


class Folder:
    def __init__(self, path: str):
        self.path = path

    def get_transactions_between_dates(self, query_range: MonthRange):
        filenames = get_filenames(self.path)
        ranges = get_filenames_between_dates(query_range, filenames)

        transactions = []
        for range in ranges:
            full_path = os.path.join(self.path, range)
            csv_transactions = get_transactions_in_csv(full_path)

            for transaction in csv_transactions:
                if query_range.contains_date(transaction.date):
                    transactions.append(transaction)

        return transactions
