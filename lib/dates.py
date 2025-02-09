from datetime import datetime, timedelta


def format_date(month_str: str, year_str: str):
    month = get_month_value(month_str)
    year = int(year_str)
    return datetime(year, month, 1)


MONTH_ABBREVIATIONS = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}


def get_month_value(month_abbreviation: str):
    return MONTH_ABBREVIATIONS.get(month_abbreviation, None)


def get_month_abbreviation(value: int):
    for key in MONTH_ABBREVIATIONS.keys():
        if MONTH_ABBREVIATIONS[key] == value:
            return key
    raise Exception("Could not find key")


def get_last_date_in_month(month: int, year: int):
    month_following = datetime(year, month, 28) + timedelta(days=4)
    return month_following.replace(day=1) - timedelta(days=1)
