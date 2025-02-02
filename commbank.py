from typing import List
from pypdf import PdfReader
from dates import parse_dashed_month_range
from files import manage_files
from search import search


INPUT_PATH = "data/Commbank/raw"
OUTPUT_PATH = "data/Commbank"


def get_page_data(reader: PdfReader):
    return [page.extract_text(extraction_mode="layout") for page in reader.pages]


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


def get_data(reader: PdfReader, month_range: List[str]):
    page_data = get_page_data(reader)
    transaction_pages = get_transaction_pages(page_data)
    lines = get_transaction_lines(transaction_pages)
    for line in lines:
        print(line)

    return []


if __name__ == "__main__":
    manage_files(INPUT_PATH, OUTPUT_PATH, get_month_range, get_data)
