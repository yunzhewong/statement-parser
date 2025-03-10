from datetime import datetime
from lib.MonthRange import MonthRange


def test_same_year():
    year = 2024
    month_range = MonthRange(datetime(year, 1, 1), datetime(year, 1, 6))
    for month in range(1, 7):
        assert month_range.get_year_in_range(month) == year


def test_different_year():
    low_year = 2023
    high_year = 2024
    month_range = MonthRange(datetime(low_year, 8, 1), datetime(high_year, 4, 1))
    for month in range(8, 13):
        assert month_range.get_year_in_range(month) == low_year
    for month in range(0, 5):
        assert month_range.get_year_in_range(month) == high_year
