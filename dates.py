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
