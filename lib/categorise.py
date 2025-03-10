from enum import Enum

from lib.transaction import Transaction, TransactionType


class Category(Enum):
    TransferIn = "Transfers In"
    TransferOut = "Transfers Out"
    Interest = "Interest"
    Cashback = "Cashback"
    Salary = "Salary"
    Investments = "Investments"

    Transport = "Transport"
    Utilities = "Utilities"
    Groceries = "Groceries"
    Entertainment = "Entertainment"


def category_is_positive(category: Category):
    return category in [
        Category.TransferIn,
        Category.Interest,
        Category.Cashback,
        Category.Salary,
    ]


def print_based_on_category():
    pass


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

    if "agl" in lowered:
        return Category.Utilities

    if "coles" in lowered or "woolworths" in lowered:
        return Category.Groceries

    return None


def categorise_transaction(transaction: Transaction):
    type_category = get_category_from_type(transaction.type)
    if type_category is not None:
        return type_category

    desc_category = get_category_from_description(transaction.description)
    if desc_category is not None:
        return desc_category

    return None
