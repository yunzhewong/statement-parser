from datetime import datetime
from typing import List
from pypdf import PdfReader
from dates import get_month_value, get_year_value
from files import get_password, manage_files
from printing import warning_print
from transaction import Transaction, TransactionType, parse_money


INPUT_PATH = "data/Coles/raw"
OUTPUT_PATH = "data/Coles"
PASSWORD = get_password("coles")


def get_page_text(reader: PdfReader):
    return [page.extract_text(extraction_mode="layout") for page in reader.pages]


def get_transaction_page_text(reader: PdfReader):
    output = []

    for page in reader.pages[1:]:

        page_text = page.extract_text(extraction_mode="layout")
        if "Transactions" in page_text:
            output.append(page_text)

    return output


def extract_date(line: str):
    separated = line.split(" ")

    if len(separated) < 2:
        raise Exception("Expected full statement date")

    full_month_string = separated[-2]
    short_month = full_month_string[0:3]

    full_year_string = separated[-1]
    short_year = full_year_string[-2:]

    return short_month + short_year


def extract_statement_dates(page: str):
    begin_start_index = page.find("Statement Begins")
    begin_finish_index = page.find("\n", begin_start_index)
    start_date = extract_date(page[begin_start_index:begin_finish_index])

    end_start_index = page.find("Statement Ends")
    end_finish_index = page.find("\n", end_start_index)
    end_date = extract_date(page[end_start_index:end_finish_index])

    return [start_date, end_date]


def get_transaction_details(value: float, desc: str):
    if desc == "Bpay Payments":
        return -1 * value, TransactionType.TransferIn

    if value < 0:
        return -1 * value, TransactionType.Credit
    return value, TransactionType.CardPayment


def parse_transaction(line: str, month_range: List[str]):
    separated = line.strip().split(" ")

    month_string = separated[0]
    month = get_month_value(month_string)

    if month is None:
        warning_print(f"NO DATE: {line}")
        return None
    day = int(separated[1])
    year_value = get_year_value(month_string, month_range)

    date = datetime(year_value, month, day)

    reverse_index = len(separated) - 1
    value = parse_money(separated[reverse_index])

    forward_index = 2
    while separated[forward_index] == "":
        forward_index += 1

    # skip the amount
    space_skips = False
    reverse_index -= 1
    while separated[reverse_index] == "":
        space_skips = True
        reverse_index -= 1

    if not space_skips:
        warning_print(f"NO AMOUNT: {line}")
        return None

    # skip the reference
    space_skips = False
    reverse_index -= 1
    while separated[reverse_index] == "":
        space_skips = True
        reverse_index -= 1

    if not space_skips:
        warning_print(f"NO AMOUNT: {line}")
        return None

    description = " ".join(separated[forward_index : reverse_index + 1])
    amount, type = get_transaction_details(value, description)

    return Transaction(date, amount, type, description)


def extract_transactions(page: str, month_range: List[str]):
    end_index = page.find("Closing Balance")
    if end_index == -1:
        end_index = page.find("(Continued next page)")

        if end_index == -1:
            end_index = page.find("Important Information")
            end_index -= 1
            while page[end_index] != "\n":
                end_index -= 1
            end_index -= 1
            while page[end_index] != "\n":
                end_index -= 1

        end_index -= 1
        while page[end_index] != "\n":
            end_index -= 1

    end_index -= 1
    while page[end_index] != "\n":
        end_index -= 1

    prior_line_index = page.find("Card Number")
    if prior_line_index == -1:
        prior_line_index = page.find("Date")
    start_index = page.find("\n", prior_line_index) + 1

    lines = page[start_index:end_index].split("\n")

    results = [parse_transaction(l, month_range) for l in lines]

    return list(filter(lambda x: x is not None, results))


def extract_data(transaction_page_text: List[str]):
    month_range = extract_statement_dates(transaction_page_text[0])
    transactions = []
    for page in transaction_page_text:
        transactions += extract_transactions(page, month_range)

    return month_range, transactions


def get_pdf_data(pdf: PdfReader):
    if not pdf.decrypt(PASSWORD):
        raise Exception("PDF Not Decryptable")

    transaction_page_text = get_transaction_page_text(pdf)

    return extract_data(transaction_page_text)


if __name__ == "__main__":
    manage_files(INPUT_PATH, OUTPUT_PATH, get_pdf_data)
