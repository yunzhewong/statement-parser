from datetime import datetime
from typing import List
from pypdf import PdfReader
from dates import get_month_abbreviation
from files import get_layout_page_data, manage_files
from search import search
from transaction import Transaction, TransactionType, parse_money


INPUT_EVERYDAY = "data/ING/Everyday/raw"
OUTPUT_EVERYDAY = "data/ING/Everyday"


class ValidationData:
    def __init__(self, numbers: List[float]):
        self.opening = numbers[0]
        self.credits = numbers[1]
        self.debits = numbers[2]
        self.closing = numbers[3]


def get_validation_line(first_page: str):
    closing_balance_index = first_page.find("Closing balance")
    closing_balance_newline = first_page.find("\n", closing_balance_index) + 1

    while first_page[closing_balance_newline] == "\n":
        closing_balance_newline += 1
    next_newline = first_page.find("\n", closing_balance_newline)
    return first_page[closing_balance_newline:next_newline]


def get_validation_numbers(line: str):
    split = list(filter(lambda x: x != "", line.split(" ")))
    return [parse_money(s[1:]) for s in split]


def get_validation_data(first_page: str):
    validation_line = get_validation_line(first_page)
    numbers = get_validation_numbers(validation_line)


def get_month_string(first_page: str):
    statement_start = first_page.find("Statement from: ")
    start_index = first_page.find(":", statement_start) + 2

    end_index = first_page.find("\n", start_index)
    return first_page[start_index:end_index].strip()


def convert_ddmmyyyy_to_abryy(ddmmyyyy: str):
    _day, month_value, year_value = ddmmyyyy.split("/")
    month_abr = get_month_abbreviation(int(month_value))
    yy = year_value[2:]
    return month_abr + yy


def get_month_range(first_page: str):
    month_string = get_month_string(first_page)
    dates = month_string.split(" to ")
    return [convert_ddmmyyyy_to_abryy(date) for date in dates]


def get_transaction_pages(page_data: List[str]):
    pages = []
    for page in page_data:
        if "Money out $" in page and "Money in $" in page:
            pages.append(page)
    return pages


def get_transaction_lines(transaction_pages: List[str]):
    transaction_lines = []
    for i in range(len(transaction_pages)):
        page = transaction_pages[i]
        balance_index = page.find("Balance $")
        start_index = page.find("\n", balance_index) + 1

        end_index = page.find("Total Cashback Financial Year to Date:")

        if end_index == -1:
            end_index = page.find("Statement continued over")
        end_index, _ = search(list(page), end_index, -1, lambda x: x != "\n")
        transaction_lines += list(
            filter(lambda x: x != "", page[start_index:end_index].split("\n"))
        )

    return transaction_lines


def extract_desc_from_item(last_item: str):
    start_index = last_item.find(".") + 3

    return last_item[start_index:]


def read_line_data(line: str):
    trimmed = line.strip()
    if len(trimmed) < 3 or trimmed[2] != "/":
        return None, trimmed, None, None

    split_and_filtered = list(filter(lambda x: x != "", trimmed.split("  ")))
    stripped = [s.strip() for s in split_and_filtered]

    date = datetime.strptime(stripped[0], "%d/%m/%Y")
    value = parse_money(stripped[1])
    transaction_desc = extract_desc_from_item(stripped[2])
    return date, None, value, transaction_desc


def get_type_and_amount(amount: float, transaction_desc: str):
    if "Osko Deposit" in transaction_desc or "Internal Transfer" in transaction_desc:
        if amount < 0:
            return TransactionType.TransferOut, -amount
        return TransactionType.TransferIn, amount

    if amount < 0:
        return TransactionType.CardPayment, -amount
    return TransactionType.Credit, amount


def get_transactions(lines: List[str]):

    data = None
    transactions: List[Transaction] = []

    for line in lines:
        date, desc, value, transaction_desc = read_line_data(line)

        if desc is not None:
            if data is None:
                raise Exception("Expected nonzero data")
            data = (data[0], data[1] + " " + desc, data[2], data[3])
        else:
            if data is not None:
                type, amount = get_type_and_amount(data[2], data[3])
                transactions.append(Transaction(data[0], amount, type, data[1]))
            data = (date, "", value, transaction_desc)

    return transactions


def get_data(reader: PdfReader):
    # page_data = [page.extract_text(extraction_mode="layout") for page in reader.pages]
    # with open("temp.txt", "w") as f:
    #     for page in page_data:
    #         f.write(page)
    #         f.write("####\n")
    with open("temp.txt", "r") as f:
        text = "\n".join(f.readlines())
        page_data = text.split("####\n")

    get_validation_data(page_data[0])
    month_range = get_month_range(page_data[0])

    transaction_pages = get_transaction_pages(page_data)
    transaction_lines = get_transaction_lines(transaction_pages)
    transactions = get_transactions(transaction_lines)

    # for t in transactions:
    #     print(t)

    return month_range, transactions


if __name__ == "__main__":
    manage_files(INPUT_EVERYDAY, OUTPUT_EVERYDAY, get_data)
