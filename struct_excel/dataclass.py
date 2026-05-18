# Legacy functions

from dataclasses import fields, is_dataclass
from enum import Enum
from openpyxl.workbook import Workbook


def dataclass_to_row(obj):
    row = []
    for f in fields(obj):
        value = getattr(obj, f.name)
        if isinstance(value, Enum):
            value = value.value
        row.append(value)

    return row


def write_dataclass_sheet(workbook: Workbook, sheet_name: str, data: list):
    ws = workbook.create_sheet(title=sheet_name)

    if not data:
        return

    if not is_dataclass(data[0]):
        raise ValueError(f"{sheet_name} contains non-dataclass objects")

    # Title
    headers = [f.name for f in fields(data[0])]
    ws.append(headers)

    # Data
    for obj in data:
        ws.append(dataclass_to_row(obj))
