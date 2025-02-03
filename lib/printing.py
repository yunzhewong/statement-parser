class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def colored_print(text: str, color: str):
    print(color + text + bcolors.ENDC)


def blue_print(text: str):
    colored_print(text, bcolors.OKBLUE)


def valid_print(text: str):
    colored_print(text, bcolors.OKGREEN)


def warning_print(text: str):
    colored_print(text, bcolors.WARNING)


def error_print(text: str):
    colored_print(text, bcolors.FAIL)
