def pad_string(item_string: str, width: int):
    return " " * (width - len(item_string)) + item_string


def float_to_money_str(val: float):
    return f"{val:.2f}"
