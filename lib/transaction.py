from datetime import datetime
from enum import Enum

from lib.strings import float_to_money_str, pad_string


class TransactionType(Enum):
    CardPayment = "Card Payment"
    Credit = "Credit"
    TransferIn = "Transfer In"
    TransferOut = "Transfer Out"
    Interest = "Interest"
    Investment = "Investment"
    Salary = "Salary"


DATE_WIDTH = 19
AMNT_WIDTH = 20
DESC_WIDTH = 120


class Transaction:
    def __init__(
        self, date: datetime, amount: float, type: TransactionType, description: str
    ):
        self.date = date
        self.amount = amount
        self.type = type
        self.description = description

    def __repr__(self):
        return f"Date: {self.date}, Desc: {self.description}, Amt: {self.amount}, Type: {self.type.value}"

    def to_data(self):
        return [
            self.date,
            self.description.replace(",", " "),
            self.amount,
            self.type.value,
        ]

    def pretty_string(self):
        desc_string = pad_string(self.description, DESC_WIDTH)
        amount_string = pad_string(float_to_money_str(self.amount), AMNT_WIDTH)
        return str(self.date) + amount_string + desc_string


def parse_money(money: str):
    return float("".join(money.split(",")))


def parse_transaction(line: str):
    trimmed = line.replace("\n", "")
    sections = trimmed.split(",")
    date = datetime.strptime(sections[0], "%Y-%m-%d %H:%M:%S")
    desc = sections[1]
    amount = float(sections[2])
    type = TransactionType(sections[3])
    return Transaction(date, amount, type, desc)


def get_transactions_in_csv(csv_filepath: str):
    with open(csv_filepath, "r") as f:
        lines = f.readlines()
        return [parse_transaction(l) for l in lines[1:]]
