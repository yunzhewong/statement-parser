import csv
from enum import Enum
import json
import sys
from typing import Dict, List, Tuple
from pypdf import PdfReader
import os
from datetime import datetime
import logging

logger = logging.getLogger("pypdf")
logger.setLevel(logging.ERROR)

INPUT_PATH = "data/HSBC/raw"
OUTPUT_PATH = "data/HSBC"

current_directory = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(current_directory, "passwords.json")) as password_file:
    passwords = json.load(password_file)
    PASSWORD = passwords["hsbc"]


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


def get_page_text(reader: PdfReader):
    return [page.extract_text(extraction_mode="layout") for page in reader.pages]


# first page contains no transaction data
PAGE_START_INDEX = 1


def get_final_page_index(page_text: List[str]):
    for i in range(PAGE_START_INDEX, len(page_text)):
        if "END OF STATEMENT" in page_text[i]:
            return i
    raise Exception("Could not find END OF STATEMENT")


def get_transaction_pages_text(pages_text: List[str]):
    final_index = get_final_page_index(pages_text)
    return pages_text[PAGE_START_INDEX : final_index + 1]


def get_transaction_text(transaction_page: str):
    date_string_index = transaction_page.find("Date")
    after_top_row_index = transaction_page.find("\n", date_string_index) + 1

    stop_index = transaction_page.find("Transaction Number")
    if stop_index == -1:
        stop_index = transaction_page.find("Important Information")

    stop_index -= 1
    while transaction_page[stop_index] == "\n":
        stop_index -= 1

    return transaction_page[after_top_row_index:stop_index]


def get_payment_transactions(transaction_text: List[str]):
    transactions = "\n".join(transaction_text)
    first_newline = transactions.find("\n")
    if first_newline == -1:
        raise Exception("Newline expected")

    closing_balance_index = transactions.find("CLOSING BALANCE")

    while transactions[closing_balance_index] != "\n":
        closing_balance_index -= 1

    transaction_lines = transactions[first_newline:closing_balance_index].split("\n")
    while "" in transaction_lines:
        transaction_lines.remove("")
    return transaction_lines


MONTH_ABBREVIATIONS = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}

DATE_STRING_LENGTH = 6


def get_year_value(month_string: str, month_range: List[str]):
    for string in month_range:
        if string.startswith(month_string):
            return int("20" + string[3:5])

    raise Exception("Expected to find year")


def line_starts_with_date(line: str, month_range: List[str]):
    if len(line) < DATE_STRING_LENGTH:
        return None

    start_index = 0
    while line[start_index] == " ":
        start_index += 1

    month_string = line[start_index + 3 : start_index + DATE_STRING_LENGTH]
    month_value = MONTH_ABBREVIATIONS.get(month_string, None)

    if month_value is None:
        return None

    year_value = get_year_value(month_string, month_range)

    day_value = int(line[start_index : start_index + 2])
    return (
        datetime(year_value, month_value, day_value),
        start_index + DATE_STRING_LENGTH + 1,
    )


def group_by_dates(transaction_lines: List[str], month_range: List[str]):
    groups: Dict[datetime, List[str]] = {}
    current_date = None

    for line in transaction_lines:
        process_data = line
        date_result = line_starts_with_date(line, month_range)

        if date_result is not None:
            (date, start_index) = date_result
            current_date = date
            process_data = line[start_index:]

        transaction_start_index = 0
        while process_data[transaction_start_index] == " ":
            transaction_start_index += 1

        if current_date is None:
            raise Exception("Should have an associated date")
        arr = groups.get(current_date, [])
        arr.append(process_data[transaction_start_index:])
        groups[current_date] = arr

    return groups


def format_description(split_desc: List[str]):
    start_index = 0
    end_index = len(split_desc)

    if split_desc[0] == "VISA" and split_desc[1] == "AUD":
        start_index += 2

    if split_desc[end_index - 1] == "AU":
        end_index -= 1
    return " ".join(split_desc[start_index:end_index]).strip()


def reformat_transaction(
    transaction: Tuple[str, int], month_range: List[str]
) -> Tuple[str, int, TransactionType]:
    capitalised_month_range = [month.upper() for month in month_range]

    desc, val = transaction
    separated_desc = desc.split(" ")
    first_string = separated_desc[0]

    remaining_desc = format_description(separated_desc[1:])

    if first_string == "EFTPOS":
        return (remaining_desc, -1 * val, TransactionType.CardPayment)
    if len(first_string) == 7 and first_string[2:] in capitalised_month_range:
        return (remaining_desc, val, TransactionType.Credit)
    if val < 0:
        return (desc, -1 * val, TransactionType.TransferOut)
    return (desc, -1 * val, TransactionType.TransferIn)


def parse_money(money: str):
    return float("".join(money.split(",")))


DESCRIPTION_CUTOFF = 60
DEBIT_CUTOFF = 120
CREDIT_CUTOFF = 160


def extract_transaction_details(line: str):
    split = line.split(" ")
    if len(split) == 0:
        raise Exception("Expected strings in payment line")
    value = parse_money(split[-1])

    if len(line) < DEBIT_CUTOFF:
        value *= -1
    description = " ".join(split[:-1]).strip()
    return (description, value)


def parse_line(payment_line: str):
    payment_line = payment_line.strip()
    if len(payment_line) < DESCRIPTION_CUTOFF:
        return payment_line, None
    if len(payment_line) < CREDIT_CUTOFF:
        return extract_transaction_details(payment_line)
    split = payment_line.split(" ")
    if len(split) == 0:
        raise Exception("Expected string in payment line")
    backtrack_index = -2
    while split[backtrack_index] == "":
        backtrack_index -= 1
    return extract_transaction_details(" ".join(split[: backtrack_index + 1]))


def identify_transactions(payments: List[str]):
    active_transaction: Tuple[str, int] | None = None

    transactions = []

    for payment in payments:
        (desc, value) = parse_line(payment)
        if value is None:
            if active_transaction is None:
                raise Exception("Transaction should be defined")
            (old_desc, trans_val) = active_transaction
            new_desc = old_desc + " " + desc
            active_transaction = (new_desc, trans_val)
        else:
            if active_transaction is not None:
                transactions.append(active_transaction)
            active_transaction = (desc, value)

    if active_transaction:
        transactions.append(active_transaction)
    return transactions


# comes in as Mmm YYYY, out as MmmYY (e.g Nov 2024 to Nov24)
def format_date(month: str, year: str):
    return month + year[2:]


def get_month_range(pages_text: List[str]):
    for page_text in pages_text:
        lines = page_text.split("\n")
        for line in lines:
            if "STATEMENT PERIOD" in line:
                separated = line.split(" ")
                items = []
                for section in separated:
                    if section == "":
                        continue
                    items.append(section)

                if len(items) < 9:
                    continue

                start = format_date(items[4], items[5])
                end = format_date(items[8], items[9])

                return [start, end]

    raise Exception("Expected Month Range")


def get_pdf_data(reader: PdfReader):
    if not reader.decrypt(PASSWORD):
        raise Exception("PDF Not Decryptable")

    pages_text = get_page_text(reader)
    month_range = get_month_range(pages_text)
    transaction_pages_text = get_transaction_pages_text(pages_text)
    transaction_text = [get_transaction_text(page) for page in transaction_pages_text]
    payment_transactions = get_payment_transactions(transaction_text)
    date_groups = group_by_dates(payment_transactions, month_range)

    parsed_transactions: List[Transaction] = []

    for date in date_groups.keys():
        payments = date_groups[date]
        transactions = identify_transactions(payments)
        formatted = [reformat_transaction(t, month_range) for t in transactions]
        for item in formatted:
            (desc, val, type) = item
            parsed_transactions.append(Transaction(date, val, type, desc))

    return month_range, parsed_transactions


if __name__ == "__main__":
    force = False
    if len(sys.argv) == 2 and sys.argv[1] == "f":
        force = True

    all_items = os.listdir(INPUT_PATH)
    filenames = [f for f in all_items if os.path.isfile(os.path.join(INPUT_PATH, f))]

    for filename in filenames:
        full_name = os.path.join(INPUT_PATH, filename)
        reader = PdfReader(full_name)
        month_range, parsed_transactions = get_pdf_data(reader)
        reader.close()

        output_name = " - ".join(month_range)
        pdf_name = output_name + ".pdf"
        csv_name = output_name + ".csv"
        if not force and output_name + ".pdf" == filename:
            print(f"{output_name} skipped")
            continue

        os.rename(full_name, os.path.join(INPUT_PATH, pdf_name))

        csv_path = os.path.join(OUTPUT_PATH, csv_name)
        if os.path.isfile(csv_path):
            os.remove(csv_path)

        data = [["Date", "Description", "Amount", "Type"]]
        for transaction in parsed_transactions:
            data.append(transaction.to_data())

        with open(csv_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(data)

        print(f"{output_name} written, {len(parsed_transactions)} transactions")
