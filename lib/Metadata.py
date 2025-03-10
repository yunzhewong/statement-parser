from dataclasses import dataclass
from typing import List
from lib.SingleMonthRange import SingleMonthRange
from lib.files import export_to_csv
from lib.printing import valid_print


@dataclass
class Metadata:
    single_month_range: SingleMonthRange
    missing_sources: List[str]

    def to_data(self):
        return [
            self.single_month_range.year,
            self.single_month_range.month,
        ] + self.missing_sources


def metadata_to_csv(output_path: str, name: str, metadata: List[Metadata]):
    data = []
    for item in metadata:
        data.append(item.to_data())

    export_to_csv(output_path, name, data)

    valid_print(f"{name} written, {len(metadata)} metadata items")
