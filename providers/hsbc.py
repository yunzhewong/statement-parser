from typing import Dict, List, Tuple
from pypdf import PdfReader
from datetime import datetime

from lib.dates import format_date, get_month_value, get_date_string_year
from lib.files import manage_files
from lib.json_config import get_suffix, get_password

from lib.floats import float_close
from lib.printing import blue_print, valid_print
from lib.transaction import Transaction, TransactionType, parse_money


SUFFIX = get_suffix("hsbc")
PASSWORD = get_password("hsbc")


class ValidationData:
    def __init__(self, starting_balance, ending_parameters):
        self.starting_balance = starting_balance
        (closing_balance, total_debits, total_credits, debit_count, credit_count) = (
            ending_parameters
        )
        self.closing_balance = closing_balance
        self.total_debits = total_debits
        self.total_credits = total_credits
        self.debit_count = debit_count
        self.credit_count = credit_count

        balance_difference = self.closing_balance - self.starting_balance
        transaction_difference = self.total_credits - self.total_debits
        assert float_close(balance_difference, transaction_difference)

    def check(self, transactions: List[Transaction]):
        change_in_balance: float = 0
        debit_sum: float = 0
        credit_sum: float = 0
        debit_count: int = 0
        credit_count: int = 0

        for transaction in transactions:
            change = transaction.amount

            if transaction.type in [
                TransactionType.CardPayment,
                TransactionType.TransferOut,
            ]:
                change *= -1
                debit_sum += transaction.amount
                debit_count += 1
            else:
                credit_sum += transaction.amount
                credit_count += 1

            change_in_balance += change

        assert debit_count == self.debit_count
        valid_print(f"Debit Count: {debit_count} / {self.debit_count}")
        assert credit_count == self.credit_count
        valid_print(f"Credit Count: {credit_count} / {self.credit_count}")

        assert float_close(debit_sum, self.total_debits)
        valid_print(f"Debit Sum: {debit_sum:.2f} / {self.total_debits:.2f}")

        assert float_close(credit_sum, self.total_credits)
        valid_print(f"Debit Sum: {credit_sum:.2f} / {self.total_credits:.2f}")

        expected_change = self.closing_balance - self.starting_balance
        assert float_close(change_in_balance, expected_change)
        valid_print(
            f"Change In Balance: {change_in_balance:.2f} / {expected_change:.2f}"
        )


def get_page_text(reader: PdfReader):
    return [page.extract_text(extraction_mode="layout") for page in reader.pages]


# first page contains no transaction data
PAGE_START_INDEX = 1


def get_final_page_index(page_text: List[str]):
    for i in range(PAGE_START_INDEX, len(page_text)):
        if "END OF STATEMENT" in page_text[i]:
            return i
    raise Exception("Could not find END OF STATEMENT")


def get_transaction_pages_text(pages_text: List[str]):
    final_index = get_final_page_index(pages_text)
    return pages_text[PAGE_START_INDEX : final_index + 1]


def get_transaction_text(transaction_page: str):
    date_string_index = transaction_page.find("Date")
    after_top_row_index = transaction_page.find("\n", date_string_index) + 1

    stop_index = transaction_page.find("END OF STATEMENT")
    if stop_index == -1:
        stop_index = transaction_page.find("Important Information")

    stop_index -= 1
    while transaction_page[stop_index] == "\n":
        stop_index -= 1

    return transaction_page[after_top_row_index : stop_index + 1]


def get_transaction_lines(transaction_text: List[str]):
    transactions = "\n".join(transaction_text)
    first_newline = transactions.find("\n")

    starting_lines = transactions[:first_newline]
    if first_newline == -1:
        raise Exception("Newline expected")

    closing_balance_index = transactions.find("CLOSING BALANCE")
    ending_lines = transactions[closing_balance_index:]

    while transactions[closing_balance_index] != "\n":
        closing_balance_index -= 1

    transaction_lines = transactions[first_newline:closing_balance_index].split("\n")
    while "" in transaction_lines:
        transaction_lines.remove("")
    return starting_lines, transaction_lines, ending_lines


def get_last_item_as_money(line: str):
    return parse_money(line.split(" ")[-1])


def get_starting_balance(line: str):
    return get_last_item_as_money(line)


def get_closing_balance(line: str):
    return get_last_item_as_money(line)


def split_to_separated_line(line: str):
    separated = line.split(" ")
    return list(filter(lambda x: x != "", separated))


def get_transaction_totals(line: str):
    separated = split_to_separated_line(line)

    debits = parse_money(separated[2])
    credits = parse_money(separated[3])

    return debits, credits


def get_transaction_counts(line: str):
    separated = split_to_separated_line(line)

    return int(separated[2]), int(separated[3])


def get_ending_parameters(ending_lines: str):
    lines = ending_lines.split("\n")

    closing_balance = get_closing_balance(lines[0])
    total_debits, total_credits = get_transaction_totals(lines[1])
    debit_count, credit_count = get_transaction_counts(lines[2])

    return closing_balance, total_debits, total_credits, debit_count, credit_count


def get_validation_data(starting_lines: str, ending_lines: str):
    starting_balance = get_starting_balance(starting_lines)
    ending_parameters = get_ending_parameters(ending_lines)
    return ValidationData(starting_balance, ending_parameters)


DATE_STRING_LENGTH = 6


def line_starts_with_date(line: str, month_range: List[str]):
    if len(line) < DATE_STRING_LENGTH:
        return None

    start_index = 0
    while line[start_index] == " ":
        start_index += 1

    month_string = line[start_index + 3 : start_index + DATE_STRING_LENGTH]

    month_value = get_month_value(month_string)

    if month_value is None:
        return None

    year_value = get_date_string_year(month_string, month_range)

    day_value = int(line[start_index : start_index + 2])
    return (
        datetime(year_value, month_value, day_value),
        start_index + DATE_STRING_LENGTH + 1,
    )


def group_by_dates(transaction_lines: List[str], month_range: List[str]):
    groups: Dict[datetime, List[str]] = {}
    current_date = None

    for line in transaction_lines:
        process_data = line
        date_result = line_starts_with_date(line, month_range)

        if date_result is not None:
            (date, start_index) = date_result
            current_date = date
            process_data = line[start_index:]

        transaction_start_index = 0
        while process_data[transaction_start_index] == " ":
            transaction_start_index += 1

        if current_date is None:
            raise Exception("Should have an associated date")
        arr = groups.get(current_date, [])
        arr.append(process_data[transaction_start_index:])
        groups[current_date] = arr

    return groups


def format_description(split_desc: List[str]):
    start_index = 0
    end_index = len(split_desc)

    if split_desc[0] == "VISA" and split_desc[1] == "AUD":
        start_index += 2

    if split_desc[end_index - 1] == "AU":
        end_index -= 1
    return " ".join(split_desc[start_index:end_index]).strip()


def reformat_transaction(
    transaction: Tuple[str, int], month_range: List[str]
) -> Tuple[str, int, TransactionType]:
    capitalised_month_range = [month.upper() for month in month_range]

    desc, val = transaction
    separated_desc = desc.split(" ")
    first_string = separated_desc[0]

    remaining_desc = format_description(separated_desc[1:])

    if first_string == "EFTPOS":
        return (remaining_desc, -1 * val, TransactionType.CardPayment)
    if len(first_string) == 7 and first_string[2:] in capitalised_month_range:
        return (remaining_desc, val, TransactionType.Credit)
    if val < 0:
        return (desc, -1 * val, TransactionType.TransferOut)
    return (desc, val, TransactionType.TransferIn)


DESCRIPTION_CUTOFF = 60
DEBIT_CUTOFF = 120
CREDIT_CUTOFF = 160


def extract_transaction_details(line: str):
    split = line.split(" ")
    if len(split) == 0:
        raise Exception("Expected strings in payment line")
    value = parse_money(split[-1])

    if len(line) < DEBIT_CUTOFF:
        value *= -1
    description = " ".join(split[:-1]).strip()
    return (description, value)


def parse_line(payment_line: str):
    payment_line = payment_line.strip()
    if len(payment_line) < DESCRIPTION_CUTOFF:
        return payment_line, None
    if len(payment_line) < CREDIT_CUTOFF:
        return extract_transaction_details(payment_line)
    split = payment_line.split(" ")
    if len(split) == 0:
        raise Exception("Expected string in payment line")
    backtrack_index = -2
    while split[backtrack_index] == "":
        backtrack_index -= 1
    return extract_transaction_details(" ".join(split[: backtrack_index + 1]))


def identify_transactions(payments: List[str]):
    active_transaction: Tuple[str, int] | None = None

    transactions = []

    for payment in payments:
        (desc, value) = parse_line(payment)
        if value is None:
            if active_transaction is None:
                raise Exception("Transaction should be defined")
            (old_desc, trans_val) = active_transaction
            new_desc = old_desc + " " + desc
            active_transaction = (new_desc, trans_val)
        else:
            if active_transaction is not None:
                transactions.append(active_transaction)
            active_transaction = (desc, value)

    if active_transaction:
        transactions.append(active_transaction)
    return transactions


def get_month_range(reader: PdfReader):
    if not reader.decrypt(PASSWORD):
        raise Exception("PDF Not Decryptable")

    pages_text = get_page_text(reader)
    for page_text in pages_text:
        lines = page_text.split("\n")
        for line in lines:
            if "STATEMENT PERIOD" in line:
                separated = line.split(" ")
                items = []
                for section in separated:
                    if section == "":
                        continue
                    items.append(section)

                if len(items) < 9:
                    continue

                start = format_date(items[4], items[5])
                end = format_date(items[8], items[9])

                return [start, end]

    raise Exception("Expected Month Range")


def get_pdf_data(reader: PdfReader, month_range: List[str]):
    if not reader.decrypt(PASSWORD):
        raise Exception("PDF Not Decryptable")

    pages_text = get_page_text(reader)
    transaction_pages_text = get_transaction_pages_text(pages_text)
    transaction_text = [get_transaction_text(page) for page in transaction_pages_text]
    start, transaction_lines, end = get_transaction_lines(transaction_text)
    validation_data = get_validation_data(start, end)
    date_groups = group_by_dates(transaction_lines, month_range)

    parsed_transactions: List[Transaction] = []

    for date in date_groups.keys():
        payments = date_groups[date]
        transactions = identify_transactions(payments)
        formatted = [reformat_transaction(t, month_range) for t in transactions]
        for item in formatted:
            (desc, val, type) = item
            parsed_transactions.append(Transaction(date, val, type, desc))

    validation_data.check(parsed_transactions)

    return parsed_transactions


def handle_hsbc():
    blue_print("HSBC")
    manage_files(SUFFIX, get_month_range, get_pdf_data)
    print()


if __name__ == "__main__":
    handle_hsbc()
