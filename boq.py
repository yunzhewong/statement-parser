from datetime import datetime
from typing import List, Tuple
from pypdf import PdfReader

from dates import get_date_string_month, get_month_value, get_date_string_year
from files import get_layout_page_data, manage_files

from floats import float_close
from printing import valid_print
from search import search
from transaction import Transaction, TransactionType, parse_money


INPUT_PATH_EVERYDAY = "data/BOQ/Everyday/raw"
OUTPUT_PATH_EVERYDAY = "data/BOQ/Everyday"

INPUT_PATH_SAVINGS = "data/BOQ/Savings/raw"
OUTPUT_PATH_SAVINGS = "data/BOQ/Savings"


class ValidationData:
    def __init__(
        self,
        open_balance: float,
        total_credits: float,
        total_debits: float,
        closing_balance: float,
    ):
        self.open_balance = open_balance
        self.total_credits = total_credits
        self.total_debits = total_debits
        self.closing_balance = closing_balance

    def check(self, transactions: List[Transaction]):
        balance_difference = self.closing_balance - self.open_balance
        total_difference = self.total_credits - self.total_debits
        assert float_close(balance_difference, total_difference)
        valid_print(
            f"Statement Differences: {total_difference:.2f} / {balance_difference:.2f}"
        )

        credits = 0.0
        debits = 0.0
        for transaction in transactions:
            if transaction.type in [
                TransactionType.CardPayment,
                TransactionType.TransferOut,
            ]:
                debits += transaction.amount
            else:
                credits += transaction.amount

        assert float_close(debits, self.total_debits)
        valid_print(f"Total Debits: {debits:.2f} / {self.total_debits:.2f}")

        assert float_close(credits, self.total_credits)
        valid_print(f"Total Credits: {credits:.2f} / {self.total_credits:.2f}")


def get_validation_value(first_page: str, text: str):
    begin = first_page.find(text)
    while first_page[begin] != "$":
        begin += 1
    begin += 1

    end = first_page.find("\n", begin)
    return parse_money(first_page[begin:end].strip())


def get_validation_data(first_page: str):

    opening_balance = get_validation_value(first_page, "Opening balance")
    total_credits = get_validation_value(first_page, "Total credits")
    total_debits = get_validation_value(first_page, "Total debits")
    closing_balance = get_validation_value(first_page, "Closing balance")

    return ValidationData(opening_balance, total_credits, total_debits, closing_balance)


def extract_dates_string(first_page: str):
    statement_period_index = first_page.find("Statement period")
    start_index, _ = search(
        list(first_page), statement_period_index, 1, lambda x: x != "\n"
    )
    start_index += 1
    start_index, _ = search(list(first_page), start_index + 1, 1, lambda x: x == " ")

    end_index = first_page.find("\n", start_index)
    return first_page[start_index:end_index]


def extract_month_string(month_abbreviation: str, year_string: str):
    return month_abbreviation + year_string[2:]


def dates_string_to_month_range(dates_string: str):
    separated = dates_string.strip().split(" ")

    if len(separated) != 7:
        raise Exception("Expected 7 Elements")

    start = extract_month_string(separated[1], separated[2])
    end = extract_month_string(separated[5], separated[6])
    return [start, end]


def get_month_range(first_page: str):
    dates_string = extract_dates_string(first_page)
    return dates_string_to_month_range(dates_string)


def get_transaction_pages(pages: List[str]):
    output = []
    for page in pages:
        keywords = ["Date", "Processed", "Description", "Debits"]
        all_found = True
        for keyword in keywords:
            if keyword not in page:
                all_found = False

        if all_found:
            output.append(page)
    return output


def formatted_line(l: str):
    output = ""
    i = 0
    while i < len(l):
        if l[i : i + len("NA")] == "NA":
            i += 2
        if l[i : i + len("N/A")] == "N/A":
            i += 3

        if i > len(l) - 1:
            break
        output += l[i]
        i += 1
    return output[:120].strip()


def get_transaction_lines(pages: List[str]):
    lines = []

    for page in pages:
        balance_index = page.find("Balance ($)")
        start_index = page.find("\n", balance_index)

        end_index = page.find("Bank of Queensland Limited ABN")

        if end_index == -1:
            end_index = page.find("Page")

        page_lines = page[start_index:end_index].split("\n")
        formatted_lines = [formatted_line(l) for l in page_lines]
        lines += list(filter(lambda x: len(x) != 0, formatted_lines))

    return lines[2:]


def get_items(separated: List[str]):
    return list(filter(lambda x: x != "", separated))


def read_date(date_string: str, month_range: List[str]):
    separated = date_string.split("-")
    if len(separated) != 2:
        raise Exception("Expected two items")
    day = int(separated[0])
    month = get_month_value(separated[1])
    low_year = get_date_string_year(month_range[0], month_range)
    high_year = get_date_string_year(month_range[1], month_range)

    low_month = get_date_string_month(month_range[0])
    high_month = get_date_string_month(month_range[1])

    if month > low_month:
        if month < high_month:
            return datetime(low_year, month, day)
    return datetime(high_year, month, day)


def get_amount(items: List[str]):
    if len(items) == 5:
        return parse_money(items[-2].strip())
    return parse_money(items[-1].strip())


def read_transaction_data(line: str, month_range: List[str]):
    separated = line.split("  ")
    items = get_items(separated)

    if len(items) == 1:
        return None, items[0], None

    date = read_date(items[0], month_range)

    return date, items[2], get_amount(items)


def get_transaction_type_and_amount(value: float, desc: str):
    if "Interest" in desc:
        return TransactionType.Interest, value

    lowercase_desc = desc.lower()
    if "future saver" in lowercase_desc or "yun zhe wong" in lowercase_desc:
        if value < 0:
            return TransactionType.TransferOut, -value
        return TransactionType.TransferIn, value

    if value < 0:
        return TransactionType.CardPayment, -value
    return TransactionType.Credit, value


def format_transaction(data: Tuple[datetime, str, float]):
    type, amount = get_transaction_type_and_amount(data[2], data[1])
    return Transaction(data[0], amount, type, data[1])


def extract_transactions(lines: List[str], month_range: List[str]):
    data = None

    transactions = []

    for line in lines:
        date, desc, value = read_transaction_data(line, month_range)

        if date is None:
            if data is None:
                raise Exception("Expected data")

            data = data[0], data[1] + " " + desc, data[2]
            continue

        if data is not None:
            transactions.append(format_transaction(data))
        data = date, desc, value

    if data is not None:
        transactions.append(format_transaction(data))

    return transactions


def get_data(reader: PdfReader):
    pages = get_layout_page_data(reader)
    validation_data = get_validation_data(pages[0])
    month_range = get_month_range(pages[0])
    transaction_pages = get_transaction_pages(pages)
    transaction_lines = get_transaction_lines(transaction_pages)
    transactions = extract_transactions(transaction_lines, month_range)

    validation_data.check(transactions)

    return month_range, transactions


if __name__ == "__main__":
    manage_files(INPUT_PATH_EVERYDAY, OUTPUT_PATH_EVERYDAY, get_data)
    manage_files(INPUT_PATH_SAVINGS, OUTPUT_PATH_SAVINGS, get_data)
