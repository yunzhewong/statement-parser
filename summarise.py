import os
import sys
from typing import List

from lib.SingleMonthRange import SingleMonthRange
from lib.TransactionGroups import parse_transaction_groups
from lib.transaction import get_transactions_in_csv


def parse_args(args: List[str]):
    year = int(args[0])
    month = int(args[1])
    return year, month


def get_transaction_csv_path(year: int, month: int):
    month_range = SingleMonthRange(month=month, year=year).to_month_range()
    filename = month_range.to_filename()
    return os.path.join("data", f"{filename}.csv")


if __name__ == "__main__":
    year, month = parse_args(sys.argv[1:])
    path = get_transaction_csv_path(year, month)
    transactions = get_transactions_in_csv(path)
    transaction_groups = parse_transaction_groups(transactions)
    transaction_groups.print_comprehensive_summary()
