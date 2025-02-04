import json
import os


def get_json(filename: str):
    current_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    with open(os.path.join(current_directory, filename)) as file:
        return json.load(file)


def get_json_value(filename: str, key: str):
    dict = get_json(filename)
    return dict[key]


def get_password(key: str) -> str:
    return get_json_value("passwords.json", key)


def get_suffix(key: str) -> str:
    return get_json_value("suffixes.json", key)
