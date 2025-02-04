import csv
import json
import logging
import os
import sys
from typing import Callable, List, Tuple

from pypdf import PdfReader

from lib.dates import month_range_to_file_name
from lib.printing import error_print, valid_print
from lib.transaction import Transaction

logger = logging.getLogger("pypdf")
logger.setLevel(logging.ERROR)


def should_force(argv: List[str]):
    return "f" in argv[1:]


def should_log(argv: List[str]):
    return "l" in argv[1:]


def should_quick(argv: List[str]):
    return "q" in argv[1:]


def get_filenames(path: str):
    all_items = os.listdir(path)
    return [f for f in all_items if os.path.isfile(os.path.join(path, f))]


def export_to_csv(output_path: str, name: str, transactions: List[Transaction]):
    csv_path = os.path.join(output_path, name)

    if os.path.isfile(csv_path):
        error_print(f"{name} deleted")
        os.remove(csv_path)

    data = [["Date", "Description", "Amount", "Type"]]
    for transaction in transactions:
        data.append(transaction.to_data())

    with open(csv_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(data)

    valid_print(f"{name} written, {len(transactions)} transactions")


def get_layout_page_data(reader: PdfReader):
    return [page.extract_text(extraction_mode="layout") for page in reader.pages]


def manage_files(
    suffix: str,
    get_month_range: Callable[[PdfReader], List[str]],
    get_data: Callable[[PdfReader, List[str]], List[Transaction]],
):
    force = should_force(sys.argv)
    log = should_log(sys.argv)
    quick = should_quick(sys.argv)

    input_path = suffix + "/raw"
    output_path = suffix

    filenames = get_filenames(input_path)

    for filename in filenames:
        if not force and not quick and filename_is_already_range(filename):
            print(f"{filename} skipped")
            continue

        file_path = os.path.join(input_path, filename)
        reader = PdfReader(file_path)
        month_range = get_month_range(reader)
        reader.close()

        output_name = month_range_to_file_name(month_range)
        pdf_name = output_name + ".pdf"

        if quick and pdf_name == filename:
            print(f"{output_name} skipped")
            continue
        reader = PdfReader(file_path)
        transactions = get_data(reader, month_range)

        if log:
            for transaction in transactions:
                print(transaction)

        os.rename(file_path, os.path.join(input_path, pdf_name))
        export_to_csv(output_path, output_name + ".csv", transactions)
        print()


def filename_is_already_range(filename: str):
    name = filename[: -len(".pdf")]
    if len(name) != 18:
        return False

    try:
        _low_year = int(name[0:4])
        _low_month = int(name[5:7])

        if name[8:10] != "to":
            return False

        _high_year = int(name[11:15])
        _high_month = int(name[17:18])
    except:
        return False

    return True
