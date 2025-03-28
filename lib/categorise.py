from enum import Enum

from lib.printing import blue_print, error_print, valid_print
from lib.transaction import Transaction, TransactionType


class Category(Enum):
    Interest = "Interest"
    Cashback = "Cashback"
    Salary = "Salary"

    Transport = "Transport"
    Utilities = "Utilities"
    Groceries = "Groceries"
    Entertainment = "Entertainment"

    TransferIn = "Transfers In"
    TransferOut = "Transfers Out"
    Investments = "Investments"


INCOME_CATEGORIES = [
    Category.Interest,
    Category.Cashback,
    Category.Salary,
]

EXPENSE_CATEGORIES = [
    Category.Transport,
    Category.Utilities,
    Category.Groceries,
    Category.Entertainment,
]

TRANSFER_CATEGORIES = [Category.TransferIn, Category.TransferOut, Category.Investments]


def category_is_earning(category: Category):
    return category in INCOME_CATEGORIES


def category_is_expense(category: Category):
    return category in EXPENSE_CATEGORIES


def category_is_transfer(category: Category):
    return category in TRANSFER_CATEGORIES


def print_based_on_category(category: Category, text: str):
    if category_is_transfer(category):
        blue_print(text)
    if category_is_earning(category):
        valid_print(text)
    if category_is_expense(category):
        error_print(text)


def get_category_from_type(type: TransactionType):
    if type == TransactionType.TransferIn:
        return Category.TransferIn
    if type == TransactionType.TransferOut:
        return Category.TransferOut
    if type == TransactionType.Interest:
        return Category.Interest
    if type == TransactionType.Credit:
        return Category.Cashback
    if type == TransactionType.Salary:
        return Category.Salary
    if type == TransactionType.Investment:
        return Category.Investments
    return None


def get_category_from_description(desc: str):
    lowered = desc.lower()

    if "myki" in lowered:
        return Category.Transport

    if "art mem vol" in lowered:
        return Category.Investments

    if "agl" in lowered or "*amaysimmobi" in lowered:
        return Category.Utilities

    if "coles" in lowered or "woolworths" in lowered or "aldi" in lowered:
        return Category.Groceries

    if "metro petroleum" in lowered:
        return Category.Transport

    return None


def categorise_transaction(transaction: Transaction):
    type_category = get_category_from_type(transaction.type)
    if type_category is not None:
        return type_category

    desc_category = get_category_from_description(transaction.description)
    if desc_category is not None:
        return desc_category

    return None
