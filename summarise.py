import os
import sys
from typing import List

from lib.SingleMonthRange import SingleMonthRange
from lib.TransactionHeader import parse_transaction_header
from lib.categorise import Category
from lib.printing import valid_print
from lib.transaction import Transaction, get_transactions_in_csv
from organise import form_groups


def parse_args(args: List[str]):
    year = int(args[0])
    month = int(args[1])
    return year, month


def get_transaction_csv_path(year: int, month: int):
    month_range = SingleMonthRange(month=month, year=year).to_month_range()
    filename = month_range.to_filename()
    return os.path.join("data", f"{filename}.csv")


def print_group(category: Category, transactions: List[Transaction]):
    transaction_header = parse_transaction_header(category, transactions)
    valid_print(transaction_header.pretty_string())

    for t in transactions:
        print(t.pretty_string())


def long_summary(transactions: List[Transaction]):
    groups = form_groups(transactions)

    for category in groups.keys():
        print_group(category, groups[category])
        print()


if __name__ == "__main__":
    year, month = parse_args(sys.argv[1:])
    path = get_transaction_csv_path(year, month)
    transactions = get_transactions_in_csv(path)
    long_summary(transactions)
