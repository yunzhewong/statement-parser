import csv
import json
import os
import sys
from typing import Callable, List, Tuple

from pypdf import PdfReader

from dates import month_range_to_file_name
from printing import error_print, valid_print
from transaction import Transaction


def should_force(argv: List[str]):
    return "f" in argv[1:]


def should_log(argv: List[str]):
    return "l" in argv[1:]


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


def get_password(key: str) -> str:
    current_directory = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_directory, "passwords.json")) as password_file:
        passwords = json.load(password_file)
        return passwords[key]
    raise Exception("Fill passwords.json")


def get_layout_page_data(reader: PdfReader):
    return [page.extract_text(extraction_mode="layout") for page in reader.pages]


def manage_files(
    input_path: str,
    output_path: str,
    get_data: Callable[[PdfReader], Tuple[List[str], List[Transaction]]],
):
    force = should_force(sys.argv)
    log = should_log(sys.argv)
    filenames = get_filenames(input_path)

    for filename in filenames:
        file_path = os.path.join(input_path, filename)
        reader = PdfReader(file_path)
        month_range, transactions = get_data(reader)
        reader.close()

        output_name = month_range_to_file_name(month_range)
        pdf_name = output_name + ".pdf"
        if not force and pdf_name == filename:
            print(f"{output_name} skipped")
            continue

        if log:
            for transaction in transactions:
                print(transaction)

        os.rename(file_path, os.path.join(input_path, pdf_name))
        export_to_csv(output_path, output_name + ".csv", transactions)
