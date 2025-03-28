from dataclasses import dataclass
from typing import Dict, List

from lib.categorise import (
    INCOME_CATEGORIES,
    EXPENSE_CATEGORIES,
    TRANSFER_CATEGORIES,
    Category,
    categorise_transaction,
    print_based_on_category,
)
from lib.printing import valid_print
from lib.strings import float_to_money_str, pad_string
from lib.transaction import AMNT_WIDTH, DATE_WIDTH, Transaction


def format_combined_transaction_title(text: str, transactions: List[Transaction]):
    total_value = sum([t.amount for t in transactions])
    remaining_width = DATE_WIDTH + AMNT_WIDTH - len(text)
    value_string = pad_string(float_to_money_str(total_value), remaining_width)
    return text + value_string


@dataclass
class TransactionGroups:
    dict: Dict[Category, List[Transaction]]

    def compute_totals(self):
        totals: Dict[Category, float] = {}
        for group_key in self.dict.keys():
            total = sum([t.amount for t in self.dict[group_key]])
            totals[group_key] = total
        return totals

    def print_category_type(self, name: str, categories: List[Category]):
        all_transactions: List[Transaction] = []
        for category in categories:
            all_transactions += self.dict.get(category, [])

        title = format_combined_transaction_title(name, all_transactions)
        print_based_on_category(categories[0], title)
        for category in categories:
            self.print_group(category)

    def print_group(self, category: Category):
        transactions = self.dict.get(category, None)
        if transactions is None:
            return

        transaction_header = format_combined_transaction_title(
            category.value, transactions
        )
        print_based_on_category(category, transaction_header)

        for t in transactions:
            print(t.pretty_string())
        print()

    def print_comprehensive_summary(self):
        self.print_category_type("Income", INCOME_CATEGORIES)
        self.print_category_type("Expenses", EXPENSE_CATEGORIES)
        self.print_category_type("Transfers", TRANSFER_CATEGORIES)


def parse_transaction_groups(transactions: List[Transaction]):
    dict: Dict[Category, List[Transaction]] = {}

    for transaction in transactions:
        category = categorise_transaction(transaction)

        if category is None:
            category = Category.Entertainment

        arr = dict.get(category, [])
        arr.append(transaction)
        dict[category] = arr

    return TransactionGroups(dict=dict)
