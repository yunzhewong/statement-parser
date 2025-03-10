from typing import List
from lib.SingleMonthRange import SingleMonthRange
from lib.Folder import Folder
from lib.files import transactions_to_csv
from lib.json_config import get_json

from lib.transaction import Transaction
from summarise import short_summary

OUTPUT_PATH = "data"


known_range_with_transactions = SingleMonthRange(month=3, year=2024)


def collate_transactions(folders: List[Folder], single_month_range: SingleMonthRange):
    month_range = single_month_range.to_month_range()

    transactions: List[Transaction] = []
    for folder in folders:
        transactions += folder.get_transactions_between_dates(month_range)

    if len(transactions) == 0:
        return None

    sorted_transactions = sorted(transactions, key=lambda x: x.date)

    output_csv_name = f"{month_range.to_filename()}.csv"
    transactions_to_csv(OUTPUT_PATH, output_csv_name, sorted_transactions)

    short_summary(sorted_transactions)
    print()

    return sorted_transactions


def search_and_collate(starting_month: SingleMonthRange, direction: int):
    month = starting_month
    while True:
        result = collate_transactions(folders, month)

        if result is None:
            break

        month = month.get_incremented_copy(direction)


if __name__ == "__main__":
    suffixes: dict = get_json("suffixes.json")

    folders = [Folder(path) for path in suffixes.values()]

    search_and_collate(known_range_with_transactions, 1)
    search_and_collate(known_range_with_transactions.get_incremented_copy(-1), 1)
