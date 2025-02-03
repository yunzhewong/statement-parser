from datetime import datetime
from enum import Enum


class TransactionType(Enum):
    CardPayment = "Card Payment"
    Credit = "Credit"
    TransferIn = "Transfer In"
    TransferOut = "Transfer Out"
    Interest = "Interest"


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
        return [self.date, self.description, self.amount, self.type.value]


def parse_money(money: str):
    return float("".join(money.split(",")))


def parse_transaction(line: str):
    sections = line.split(",")

    date = datetime.strptime(sections[1], "%Y-%m-%d %H:%M:%S")
    desc = sections[2]
    amount = float(sections[3])
    type = TransactionType(sections[4])
    return Transaction(date, amount, type, desc)
