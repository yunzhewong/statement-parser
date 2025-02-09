from typing import Dict, List
from lib.Folder import Folder
from lib.MonthRange import MonthRange
from lib.files import export_to_csv
from lib.json_config import get_json
from datetime import datetime

from lib.printing import blue_print, valid_print, warning_print
from lib.transaction import Transaction, TransactionType

OUTPUT_PATH = "data"


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

    valid_print(f"Total Card Payments: {card_payments}")
    valid_print(f"Total Credits: {credits}")
    valid_print(f"Total Transfer In: {transfer_in}")
    valid_print(f"Total Transfer Out: {transfer_out}")
    valid_print(f"Total Interest: {interest}")

    warning_print(f"Total Investments (+): {investment}")
    warning_print(f"Transfer Difference (+): {transfer_in - transfer_out}")

    plus = credits + transfer_in + interest
    minus = card_payments + transfer_out + investment

    warning_print(f"Bank Balance Change (+): {plus - minus}")


if __name__ == "__main__":
    suffixes: dict = get_json("suffixes.json")

    folders = [Folder(path) for path in suffixes.values()]
    query_range = MonthRange(datetime(2024, 12, 1), datetime(2024, 12, 31))

    transactions = []
    for folder in folders:
        transactions += folder.get_transactions_between_dates(query_range)

    def sort_key(x: Transaction):
        return x.date

    sorted_transactions = sorted(transactions, key=sort_key)

    export_to_csv(OUTPUT_PATH, query_range.get_filename() + ".csv", transactions)
    log_info(sorted_transactions)
