from typing import List
from pypdf import PdfReader

from files import manage_files

from search import search


INPUT_PATH_EVERYDAY = "data/BOQ/Everyday/raw"
OUTPUT_PATH_EVERYDAY = "data/BOQ/Everyday"


def get_pages(reader: PdfReader):
    return [page.extract_text(extraction_mode="layout") for page in reader.pages]


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


def get_transaction_lines(pages: List[str]):
    lines = []

    for page in pages:
        balance_index = page.find("Balance ($)")
        start_index = page.find("\n", balance_index)

        end_index = page.find("Bank of Queensland Limited ABN")

        if end_index == -1:
            end_index = page.find("Page")

        page_lines = page[start_index:end_index].split("\n")
        trimmed_lines = [l.strip() for l in page_lines]
        lines += list(filter(lambda x: len(x) > 10, trimmed_lines))

    for line in lines:
        print(line)
    return lines


def get_data(reader: PdfReader):
    pages = get_pages(reader)

    month_range = get_month_range(pages[0])
    transaction_pages = get_transaction_pages(pages)
    get_transaction_lines(transaction_pages)
    return month_range, []


if __name__ == "__main__":
    manage_files(INPUT_PATH_EVERYDAY, OUTPUT_PATH_EVERYDAY, get_data)
