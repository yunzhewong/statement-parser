from datetime import datetime

from lib.files import get_filenames


class Folder:
    def __init__(self, path: str):
        self.path = path

    def get_transactions_between_dates(self, start: datetime, end: datetime):
        filenames = get_filenames(self.path)
        print(filenames)
