from datetime import datetime
from pypdf import PdfReader
from lib.MonthRange import MonthRange
from lib.dates import format_date, get_month_value
from lib.files import manage_files
from lib.json_config import get_suffix, get_password

from lib.printing import blue_print, warning_print
from lib.search import find_index_prior_to_newline, search
from lib.transaction import Transaction, TransactionType, parse_money


SUFFIX = get_suffix("coles")
PASSWORD = get_password("coles")


def get_page_text(reader: PdfReader):
    return [page.extract_text(extraction_mode="layout") for page in reader.pages]


def get_transaction_page_text(reader: PdfReader):
    output = []

    # first page not parsable for some reason
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
    month_string = full_month_string[0:3]

    year_string = separated[-1]
    return format_date(month_string, year_string)


def extract_month_range(page: str):
    begin_start_index = page.find("Statement Begins")
    begin_finish_index = page.find("\n", begin_start_index)
    start_date = extract_date(page[begin_start_index:begin_finish_index])

    end_start_index = page.find("Statement Ends")
    end_finish_index = page.find("\n", end_start_index)
    end_date = extract_date(page[end_start_index:end_finish_index])

    return MonthRange(start_date, end_date)


def get_transaction_details(value: float, desc: str):
    if desc == "Bpay Payments":
        return -1 * value, TransactionType.TransferIn

    if value < 0:
        return -1 * value, TransactionType.Credit
    return value, TransactionType.CardPayment


def parse_transaction(line: str, month_range: MonthRange):
    separated = line.strip().split(" ")

    month_string = separated[0]
    month = get_month_value(month_string)

    if month is None:
        warning_print(f"NO DATE: {line}")
        return None
    day = int(separated[1])
    year = month_range.get_year_in_range(month)

    date = datetime(year, month, day)

    reverse_index = len(separated) - 1
    value = parse_money(separated[reverse_index])

    forward_index, _ = search(separated, 2, 1, lambda x: x == "")

    reverse_index, count = search(separated, reverse_index - 1, -1, lambda x: x == "")

    if count == 0:
        warning_print(f"NO AMOUNT: {line}")
        return None

    reverse_index, count = search(separated, reverse_index - 1, -1, lambda x: x == "")

    if count == 0:
        warning_print(f"NO DESC: {line}")
        return None

    description = " ".join(separated[forward_index : reverse_index + 1])
    amount, type = get_transaction_details(value, description)

    return Transaction(date, amount, type, description)


def extract_transactions(page: str, month_range: MonthRange):
    end_index = page.find("Closing Balance")
    if end_index == -1:
        end_index = page.find("(Continued next page)")

        if end_index == -1:
            end_index = page.find("Important Information")
            end_index = find_index_prior_to_newline(page, end_index - 1)
            end_index = find_index_prior_to_newline(page, end_index - 1)

        end_index = find_index_prior_to_newline(page, end_index - 1)
    end_index = find_index_prior_to_newline(page, end_index - 1)

    prior_line_index = page.find("Card Number")
    if prior_line_index == -1:
        prior_line_index = page.find("Date")
    start_index = page.find("\n", prior_line_index) + 1

    lines = page[start_index:end_index].split("\n")

    results = [parse_transaction(l, month_range) for l in lines]

    return list(filter(lambda x: x is not None, results))


def decrypt_and_get_data(reader: PdfReader):
    if not reader.decrypt(PASSWORD):
        raise Exception("PDF Not Decryptable")

    return get_transaction_page_text(reader)


def get_month_range(reader: PdfReader):
    page_data = decrypt_and_get_data(reader)
    return extract_month_range(page_data[0])


def get_pdf_data(reader: PdfReader, month_range: MonthRange):
    page_data = decrypt_and_get_data(reader)

    transactions = []
    for page in page_data:
        transactions += extract_transactions(page, month_range)

    return transactions


def handle_coles():
    blue_print("COLES")
    manage_files(SUFFIX, get_month_range, get_pdf_data)
    print()


if __name__ == "__main__":
    handle_coles()
