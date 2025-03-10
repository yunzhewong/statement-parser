import os
import sys
from typing import Dict, List

from lib.categorise import Category, categorise_transaction
from lib.printing import valid_print, warning_print
from lib.transaction import Transaction, TransactionType, get_transactions_in_csv


def short_summary(transactions: List[Transaction]):
    groups = form_groups(transactions)

    totals: Dict[Category, float] = {}
    for group_key in groups.keys():
        total = sum([t.amount for t in groups[group_key]])
        totals[group_key] = total

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


def get_transactions():
    year = int(sys.argv[1])
    month = int(sys.argv[2])

    filename = f"{year}-{str(month).zfill(2)} to {year}-{str(month).zfill(2)}.csv"
    full_path = os.path.join("data", filename)
    return get_transactions_in_csv(full_path)


def form_groups(transactions: List[Transaction]):
    groups: Dict[Category, List[Transaction]] = {}

    for transaction in transactions:
        category = categorise_transaction(transaction)

        if category is None:
            category = Category.Entertainment

        arr = groups.get(category, [])
        arr.append(transaction)
        groups[category] = arr

    return groups


def print_group(category: Category, transactions: List[Transaction]):
    valid_print(category.value)

    for t in transactions:
        print(t.pretty_string())


def long_summary(transactions: List[Transaction]):
    groups = form_groups(transactions)

    for category in groups.keys():
        print_group(category, groups[category])
        print()


if __name__ == "__main__":
    transactions = get_transactions()
    long_summary(transactions)
