from datetime import datetime
from enum import Enum


class TransactionType(Enum):
    CardPayment = "Card Payment"
    Credit = "Credit"
    TransferIn = "Transfer In"
    TransferOut = "Transfer Out"
    Interest = "Interest"
    Investment = "Investment"


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
