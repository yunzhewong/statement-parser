from typing import List
from lib.Folder import Folder
from lib.json_config import get_json
from datetime import datetime


if __name__ == "__main__":
    suffixes: dict = get_json("suffixes.json")

    folders = [Folder(path) for path in suffixes.values()]

    for folder in folders:
        folder.get_transactions_between_dates(datetime.now(), datetime.now())
