"""
Header detection, type inference, and range detection for Excel workbooks.
"""

import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Set, Tuple
import openpyxl
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils import get_column_letter

from ..models.field import DataType


def infer_value_type(val: Any) -> DataType:
    """Infer the data type of a single value."""
    if val is None or val == "":
        return DataType.UNKNOWN

    if isinstance(val, (datetime, date)):
        return DataType.DATE if isinstance(val, date) and not isinstance(val, datetime) else DataType.DATETIME

    if isinstance(val, bool):
        return DataType.BOOLEAN

    if isinstance(val, int):
        return DataType.INTEGER

    if isinstance(val, float):
        return DataType.FLOAT

    val_str = str(val).strip()

    # Boolean string check
    if val_str.lower() in {"true", "false", "yes", "no", "y", "n"}:
        return DataType.BOOLEAN

    # Currency check ($1,000.00 or Rp 50.000 or €100)
    if re.match(r"^[\$€£¥Rp\s]*[\d,]+(\.\d+)?[\s€]?$", val_str) and any(c in val_str for c in "$€£¥Rp"):
        return DataType.CURRENCY

    # Percentage check
    if re.match(r"^-?[\d,]+(\.\d+)?\s*%$", val_str):
        return DataType.PERCENTAGE

    # Number check
    clean_num = val_str.replace(",", "")
    if re.match(r"^-?\d+$", clean_num):
        return DataType.INTEGER
    if re.match(r"^-?\d+\.\d+$", clean_num):
        return DataType.FLOAT

    # Date regex check (YYYY-MM-DD or DD/MM/YYYY or MM/DD/YYYY)
    if re.match(r"^\d{4}[-/.]\d{1,2}[-/.]\d{1,2}$", val_str) or re.match(r"^\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}$", val_str):
        return DataType.DATE

    return DataType.STRING


def infer_column_type(values: List[Any]) -> DataType:
    """Infer the predominant data type of a column based on non-null samples."""
    non_nulls = [v for v in values if v is not None and str(v).strip() != ""]
    if not non_nulls:
        return DataType.STRING

    type_counts: Dict[DataType, int] = {}
    for v in non_nulls:
        t = infer_value_type(v)
        if t != DataType.UNKNOWN:
            type_counts[t] = type_counts.get(t, 0) + 1

    if not type_counts:
        return DataType.STRING

    dominant_type = max(type_counts.items(), key=lambda item: item[1])[0]
    if dominant_type in (DataType.INTEGER, DataType.FLOAT):
        has_float = any(infer_value_type(v) == DataType.FLOAT for v in non_nulls)
        return DataType.FLOAT if has_float else DataType.INTEGER

    return dominant_type


def detect_header_candidates(sheet: Worksheet, max_scan_rows: int = 30) -> List[Tuple[int, float]]:
    """
    Scans the first N rows of a worksheet to score candidate header rows.
    Returns a sorted list of (row_number, confidence_score) descending.
    """
    candidates: List[Tuple[int, float]] = []
    max_row = min(sheet.max_row, max_scan_rows)
    if max_row < 1:
        return [(1, 0.5)]

    for row_idx in range(1, max_row + 1):
        row_cells = [cell for cell in sheet[row_idx] if cell.value is not None and str(cell.value).strip() != ""]
        if not row_cells:
            continue

        total_cells = len(row_cells)
        if total_cells == 0:
            continue

        # 1. Mostly strings / text
        string_count = sum(1 for c in row_cells if isinstance(c.value, str))
        string_ratio = string_count / total_cells

        # 2. Distinct values
        values = [str(c.value).strip() for c in row_cells]
        unique_ratio = len(set(v.lower() for v in values)) / total_cells

        # 3. Ratio of filled cells across sheet width
        sheet_max_col = max(sheet.max_column, 1)
        fill_ratio = min(total_cells / max(sheet_max_col, 1), 1.0)

        # 4. Check if cells contain data-like ID codes (e.g. ITM-1, SUB-1001, numbers)
        has_id_code_patterns = any(re.search(r"^[A-Za-z0-9]+[-_]\d+", v) for v in values)
        has_pure_numbers = any(re.match(r"^\d+(\.\d+)?$", v) for v in values)

        # 5. Check if next row has actual data records
        next_row_has_data = False
        if row_idx < sheet.max_row:
            next_cells = [c for c in sheet[row_idx + 1] if c.value is not None and str(c.value).strip() != ""]
            if len(next_cells) >= total_cells * 0.5:
                next_row_has_data = True

        score = (string_ratio * 0.35) + (unique_ratio * 0.25) + (fill_ratio * 0.15)
        if next_row_has_data:
            score += 0.15

        # Row 1 prior: standard spreadsheets start headers on row 1
        if row_idx == 1:
            score += 0.15

        # Penalize data code rows
        if has_id_code_patterns or has_pure_numbers:
            score -= 0.25

        # Penalize if it's a single-cell title banner spanning multiple columns
        if total_cells == 1 and sheet_max_col > 1:
            score *= 0.3

        candidates.append((row_idx, round(max(min(score, 1.0), 0.0), 3)))

    candidates.sort(key=lambda x: x[1], reverse=True)
    if not candidates:
        return [(1, 0.5)]
    return candidates
