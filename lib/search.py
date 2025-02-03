from typing import Callable, List


def search(arr: List[str], start: int, inc: int, condition: Callable[[str], bool]):
    count = 0
    while condition(arr[start]):
        start += inc
        count += 1
    return start, count


def find_index_prior_to_newline(page: str, current_index: int):
    end_index, _ = search(list(page), current_index, -1, lambda x: x != "\n")
    return end_index
