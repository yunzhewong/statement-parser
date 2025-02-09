from typing import Dict, List
from lib.printing import valid_print, warning_print
from lib.transaction import Transaction, TransactionType


def log_info(transactions: List[Transaction]):
    d: Dict[TransactionType, float] = {}

    for transaction in transactions:
        sum = d.get(transaction.type, 0)
        d[transaction.type] = sum + transaction.amount

    card_payments = d.get(TransactionType.CardPayment, 0)
    credits = d.get(TransactionType.Credit, 0)
    transfer_in = d.get(TransactionType.TransferIn, 0)
    transfer_out = d.get(TransactionType.TransferOut, 0)
    interest = d.get(TransactionType.Interest, 0)
    investment = d.get(TransactionType.Investment, 0)
    salary = d.get(TransactionType.Salary, 0)

    valid_print(f"Total Card Payments: {card_payments}")
    valid_print(f"Total Credits: {credits}")
    valid_print(f"Total Transfer In: {transfer_in}")
    valid_print(f"Total Transfer Out: {transfer_out}")
    valid_print(f"Total Interest: {interest}")
    valid_print(f"Total Salary: {salary}")

    warning_print(f"Total Investments (+): {investment}")
    warning_print(f"Transfer Difference (+): {transfer_in - transfer_out}")

    plus = credits + transfer_in + interest
    minus = card_payments + transfer_out + investment

    warning_print(f"Bank Balance Change (+): {plus - minus}")
