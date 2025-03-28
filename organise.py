from typing import Dict, List
from lib.Metadata import Metadata, metadata_to_csv
from lib.SingleMonthRange import SingleMonthRange
from lib.Folder import Folder
from lib.TransactionGroups import parse_transaction_groups
from lib.categorise import Category, categorise_transaction
from lib.files import transactions_to_csv
from lib.json_config import get_json
from lib.printing import valid_print, warning_print
from lib.transaction import Transaction

OUTPUT_PATH = "data"

known_range_with_transactions = SingleMonthRange(month=3, year=2024)


def short_summary(transactions: List[Transaction]):
    transaction_groups = parse_transaction_groups(transactions)
    totals = transaction_groups.compute_totals()

    for total_key in totals.keys():
        valid_print(f"Total {total_key.value}: {totals[total_key]}")

    warning_print(
        f"Transfer Difference (+): {totals.get(Category.TransferIn, 0) - totals.get(Category.TransferOut, 0)}"
    )

    plus = (
        totals.get(Category.Cashback, 0)
        + totals.get(Category.TransferIn, 0)
        + totals.get(Category.Salary, 0)
        + totals.get(Category.Interest, 0)
    )
    overall = sum([totals[total_key] for total_key in totals.keys()])
    minus = overall - plus

    warning_print(f"Balance Change (+): {plus - minus}")


def collate_transactions(folders: List[Folder], single_month_range: SingleMonthRange):
    month_range = single_month_range.to_month_range()

    missing_sources = set()
    transactions: List[Transaction] = []
    for folder in folders:
        source_transactions = folder.get_transactions_between_dates(month_range)
        if len(source_transactions) == 0:
            missing_sources.add(folder.get_source())
            continue
        transactions += source_transactions

    if len(transactions) == 0:
        return None

    sorted_transactions = sorted(transactions, key=lambda x: x.date)

    output_csv_name = f"{month_range.to_filename()}.csv"
    transactions_to_csv(OUTPUT_PATH, output_csv_name, sorted_transactions)

    short_summary(sorted_transactions)
    print()

    return list(missing_sources)


def search_and_collate(starting_month: SingleMonthRange, direction: int):
    metadata = []
    month = starting_month
    while True:
        missing_sources = collate_transactions(folders, month)

        if missing_sources is None:
            break

        metadata.append(
            Metadata(single_month_range=month, missing_sources=missing_sources)
        )

        month = month.get_incremented_copy(direction)
    return metadata


if __name__ == "__main__":
    suffixes: dict = get_json("suffixes.json")

    folders = [Folder(path) for path in suffixes.values()]

    forward_metadata = search_and_collate(known_range_with_transactions, 1)
    inverse_metadata = search_and_collate(
        known_range_with_transactions.get_incremented_copy(-1), -1
    )

    metadata = list(reversed(inverse_metadata)) + forward_metadata

    metadata_to_csv(OUTPUT_PATH, f"metadata.csv", metadata)
