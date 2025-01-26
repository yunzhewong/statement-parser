import csv
import json
import os
from typing import List

from transaction import Transaction


def should_force(argv: List[str]):
    if len(argv) == 2 and argv[1] == "f":
        return True
    return False


def get_filenames(path: str):
    all_items = os.listdir(path)
    return [f for f in all_items if os.path.isfile(os.path.join(path, f))]


def export_to_csv(output_path: str, name: str, transactions: List[Transaction]):
    csv_path = os.path.join(output_path, name)

    if os.path.isfile(csv_path):
        print(f"{name} deleted")
        os.remove(csv_path)

    data = [["Date", "Description", "Amount", "Type"]]
    for transaction in transactions:
        data.append(transaction.to_data())

    with open(csv_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(data)

    print(f"{name} written, {len(transactions)} transactions")


def get_password(key: str) -> str:
    current_directory = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_directory, "passwords.json")) as password_file:
        passwords = json.load(password_file)
        return passwords[key]
    raise Exception("Fill passwords.json")
