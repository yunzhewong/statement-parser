import csv
from dataclasses import dataclass
import json
import logging
import os
import sys
from typing import Callable, List, Tuple

from pypdf import PdfReader

from lib.MonthRange import MonthRange, get_month_range_from_filename
from lib.printing import error_print, valid_print
from lib.transaction import Transaction

logger = logging.getLogger("pypdf")
logger.setLevel(logging.ERROR)


@dataclass
class FileParsingArgs:
    force: bool
    log: bool
    quick: bool


def parse_manage_args(argv: List[str]):
    all_args = argv[1:]
    force = "f" in all_args
    log = "l" in all_args
    quick = "q" in all_args
    return FileParsingArgs(force=force, log=log, quick=quick)


def get_filenames(path: str):
    all_items = os.listdir(path)
    return [f for f in all_items if os.path.isfile(os.path.join(path, f))]


def transactions_to_csv(output_path: str, name: str, transactions: List[Transaction]):
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
    get_month_range: Callable[[PdfReader], MonthRange],
    get_data: Callable[[PdfReader, MonthRange], List[Transaction]],
):
    args = parse_manage_args(sys.argv)

    input_path = suffix + "/raw"
    output_path = suffix

    filenames = get_filenames(input_path)

    for filename in filenames:
        if not args.force and not args.quick and filename_is_already_range(filename):
            print(f"{filename} skipped")
            continue

        file_path = os.path.join(input_path, filename)
        reader = PdfReader(file_path)
        month_range = get_month_range(reader)
        reader.close()

        output_name = month_range.to_filename()
        pdf_name = output_name + ".pdf"

        if args.quick and pdf_name == filename:
            print(f"{output_name} skipped")
            continue
        reader = PdfReader(file_path)
        transactions = get_data(reader, month_range)

        if args.log:
            for transaction in transactions:
                print(transaction)

        os.rename(file_path, os.path.join(input_path, pdf_name))
        transactions_to_csv(output_path, output_name + ".csv", transactions)
        print()


def filename_is_already_range(filename: str):
    return get_month_range_from_filename(filename) is not None
