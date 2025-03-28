from dataclasses import dataclass
from typing import List

from lib.categorise import Category
from lib.strings import float_to_money_str, pad_string
from lib.transaction import AMNT_WIDTH, DATE_WIDTH, Transaction


@dataclass
class TransactionHeader:
    category: Category
    total_value: float

    def pretty_string(self):
        category_name = self.category.value

        # align with transaction width
        remaining_width = DATE_WIDTH + AMNT_WIDTH - len(category_name)
        value_string = pad_string(float_to_money_str(self.total_value), remaining_width)
        return category_name + value_string


def parse_transaction_header(category: Category, transactions: List[Transaction]):
    total_value = sum([t.amount for t in transactions])
    return TransactionHeader(category=category, total_value=total_value)
