from lib.SingleMonthRange import SingleMonthRange


def test_positive_increment():
    jan2024 = SingleMonthRange(1, 2024)
    feb2024 = SingleMonthRange(2, 2024)
    assert jan2024.get_incremented_copy(1) == feb2024


def test_negative_increment():
    jan2024 = SingleMonthRange(1, 2024)
    feb2024 = SingleMonthRange(2, 2024)
    assert feb2024.get_incremented_copy(-1) == jan2024


def test_positive_over_year_end():
    jan2024 = SingleMonthRange(1, 2024)
    dec2023 = SingleMonthRange(12, 2023)
    assert dec2023.get_incremented_copy(1) == jan2024


def test_negative_over_year_end():
    jan2024 = SingleMonthRange(1, 2024)
    dec2023 = SingleMonthRange(12, 2023)
    assert jan2024.get_incremented_copy(-1) == dec2023
