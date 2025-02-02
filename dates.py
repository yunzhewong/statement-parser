from datetime import datetime
from typing import List


# comes in as Mmm YYYY, out as MmmYY (e.g Nov 2024 to Nov24)
def format_date(month: str, year: str):
    return month + year[2:]


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


def month_string_to_numbers(month_string: str):
    month_value = get_month_value(month_string[:3])
    if month_value is None:
        raise Exception("Expected month value")
    month_output = str(month_value).zfill(2)
    year_value = int(month_string[3:])
    year_output = str(year_value).zfill(2)
    return f"20{year_output}-{month_output}"


def month_range_to_file_name(month_range: List[str]):
    numbers = [month_string_to_numbers(month_string) for month_string in month_range]
    return " to ".join(numbers)


def get_date_string_month(month_string: str):
    value = get_month_value(month_string[:3])
    if value is None:
        raise Exception("Value expected")
    return value


def get_date_string_year(month_string: str, month_range: List[str]):
    for string in month_range:
        if string.startswith(month_string):
            return int("20" + string[3:5])

    raise Exception("Expected to find year")


def extract_month_string(month_abbreviation: str, year_string: str):
    return month_abbreviation + year_string[2:]


def get_date_between_years(day: int, month_value: int, month_range: List[str]):
    low_year = get_date_string_year(month_range[0], month_range)
    high_year = get_date_string_year(month_range[1], month_range)

    low_month = get_date_string_month(month_range[0])
    high_month = get_date_string_month(month_range[1])
    if month_value > low_month:
        if month_value < high_month:
            return datetime(low_year, month_value, day)
    return datetime(high_year, month_value, day)


def parse_dashed_month_range(dashed_month_range: str):
    separated = dashed_month_range.split(" ")

    if len(separated) != 7:
        raise Exception("Expected 7 Elements")

    start = extract_month_string(separated[1], separated[2])
    end = extract_month_string(separated[5], separated[6])
    return [start, end]
