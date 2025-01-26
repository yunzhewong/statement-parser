from datetime import datetime
from enum import Enum


class TransactionType(Enum):
    CardPayment = "Card Payment"
    Credit = "Credit"
    TransferIn = "Transfer In"
    TransferOut = "Transfer Out"


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
