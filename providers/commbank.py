from datetime import datetime
from typing import List, Tuple
from pypdf import PdfReader
from lib.dates import get_date_between_years, get_month_value, parse_dashed_month_range
from lib.files import manage_files
from lib.floats import float_close
from lib.printing import blue_print, valid_print
from lib.search import search
from lib.transaction import Transaction, TransactionType, parse_money


SUFFIX = "data/Commbank"


class ValidationData:
    def __init__(self, numbers: List[float]):
        self.opening = numbers[0]
        self.debits = numbers[1]
        self.credits = numbers[2]
        self.closing = numbers[3]

        final_balance = self.opening + self.credits - self.debits
        assert float_close(self.closing, final_balance)
        valid_print(f"Final Balance: {final_balance} / {self.closing}")

    def check(self, transactions: List[Transaction]):
        total_credit = 0.0
        total_debit = 0.0
        for transaction in transactions:
            if transaction.type in [TransactionType.Credit, TransactionType.TransferIn]:
                total_credit += transaction.amount
            else:
                total_debit += transaction.amount

        assert float_close(self.debits, total_debit)
        valid_print(f"Total Debits: {total_debit} / {self.debits}")

        assert float_close(self.credits, total_credit)
        valid_print(f"Total Credits: {total_credit} / {self.credits}")


def split_by_bunches(line: str):
    split = line.split("  ")
    filtered = list(filter(lambda x: x != "", split))
    return [s.strip() for s in filtered]


def get_page_data(reader: PdfReader):
    return [page.extract_text(extraction_mode="layout") for page in reader.pages]


def get_validation_section(page: str):
    closing_balance_index = page.find("Closing balance")

    start_index = page.find("\n", closing_balance_index)
    while page[start_index] == "\n":
        start_index += 1

    next_newline = page.find("\n", start_index)

    if next_newline == -1:
        return page[start_index:]
    return page[start_index:next_newline]


def get_validation_numbers(sections: List[str]):
    if sections[-1] != "CR" or sections[0][-2:] != "CR":
        raise Exception("Expected CR")

    strings = [s[1:] for s in sections[:-1]]
    strings[0] = strings[0][:-2]

    return [parse_money(s) for s in strings]


def get_validation_data(page_data: List[str]):
    page = get_validation_page(page_data)
    validation_section = get_validation_section(page)
    sections = split_by_bunches(validation_section)
    numbers = get_validation_numbers(sections)
    return ValidationData(numbers)


def get_validation_page(page_data: List[str]):
    keywords = ["Opening balance", "Total debits", "Total credits", "Closing balance"]
    for page in page_data:
        all_found = True
        for keyword in keywords:
            if keyword not in page:
                all_found = False
        if all_found:
            return page

    raise Exception("Expected validation page")


def get_month_string(first_page: str):
    period_index = first_page.find("Period")

    first_space = first_page.find(" ", period_index)
    newline = first_page.find("\n", first_space)

    return first_page[first_space:newline].strip()


def get_month_range(reader: PdfReader):
    page_data = get_page_data(reader)
    month_string = get_month_string(page_data[0])
    return parse_dashed_month_range(month_string)


def get_transaction_pages(page_data: List[str]):
    keywords = ["Date", "Transaction", "Debit", "Credit", "Balance"]

    output: List[str] = []
    for page in page_data:
        all_keywords_present = True
        for keyword in keywords:
            if keyword not in page:
                all_keywords_present = False

        if all_keywords_present:
            output.append(page)
    return output


def find_newline_after_transaction_header(page: str):
    start_index = 0

    while True:
        balance_index = page.find("Balance", start_index)

        if balance_index == -1:
            raise Exception("Expected to find")
        previous_newline, _ = search(list(page), balance_index, -1, lambda x: x != "\n")
        next_newline = page.find("\n", balance_index)

        text = page[previous_newline + 1 : next_newline]
        if "Debit" in text and "Credit" in text:
            return next_newline

        start_index = balance_index + 1


def find_transaction_stop_index(page: str):
    closing_balance_index = page.find("CLOSING BALANCE")

    if closing_balance_index == -1:
        return -1

    stop_index, _ = search(list(page), closing_balance_index, -1, lambda x: x != "\n")
    return stop_index


def get_transaction_section(page: str):
    start_index = find_newline_after_transaction_header(page)
    stop_index = find_transaction_stop_index(page)

    if stop_index == -1:
        return page[start_index:]
    return page[start_index:stop_index]


def get_transaction_lines(transaction_pages: List[str]):
    lines = []

    for page in transaction_pages:
        section = get_transaction_section(page)
        split_and_filtered = list(filter(lambda s: s != "", section.split("\n")))
        trimmed = [s.strip() for s in split_and_filtered]
        lines += trimmed

    return lines


def aggregate_lines(lines: List[str], month_range: List[str]):
    aggregated: List[Tuple[datetime, str]] = []
    aggregate = None

    for line in lines:
        if len(line) >= 6:
            month_section = line[3:6]
            month_value = get_month_value(month_section)
            if month_value is not None:
                day = int(line[0:2])
                date = get_date_between_years(day, month_value, month_range)
                if aggregate is not None:
                    aggregated.append(aggregate)
                aggregate = (date, line[6:].strip())
                continue

        if aggregate is None:
            raise Exception("Expected Aggregate")
        aggregate = (aggregate[0], aggregate[1] + " " + line)
    if aggregate is not None:
        aggregated.append(aggregate)
    return aggregated


def parse_possible_dollar_signed_number(s: str):
    return parse_money(s.replace("$", ""))


def parse_amount_and_type(value: float, desc: str):
    if "Transfer" in desc:
        if value < 0:
            return -value, TransactionType.TransferOut
        return value, TransactionType.TransferIn

    if value < 0:
        return -value, TransactionType.CardPayment

    return value, TransactionType.Credit


def get_transactions(aggregated: List[Tuple[datetime, str]]):
    transactions = []
    for item in aggregated:
        date, full_str = item

        chunks = list(filter(lambda x: x != "", full_str.split("  ")))
        trimmed = [s.strip() for s in chunks]

        multiplier = -1
        if len(trimmed) == 3:
            multiplier = 1

        value = multiplier * parse_possible_dollar_signed_number(trimmed[1])
        desc = trimmed[0]
        amount, type = parse_amount_and_type(value, desc)
        transactions.append(Transaction(date, amount, type, desc))

    return transactions


def get_data(reader: PdfReader, month_range: List[str]):
    page_data = get_page_data(reader)

    validation_data = get_validation_data(page_data)

    transaction_pages = get_transaction_pages(page_data)
    lines = get_transaction_lines(transaction_pages)
    aggregated = aggregate_lines(lines, month_range)
    transactions = get_transactions(aggregated[1:])
    validation_data.check(transactions)
    return transactions


def handle_commbank():
    blue_print("COMMONWEALTH BANK")
    manage_files(SUFFIX, get_month_range, get_data)
    print()


if __name__ == "__main__":
    handle_commbank()
