"""
Robust Dynamic Excel Workbook Analyzer.
No hardcoded business parameters or column assumptions.
"""

import os
import re
from typing import Any, Dict, List, Optional, Tuple
import openpyxl
from openpyxl.cell.cell import Cell
from openpyxl.utils import get_column_letter

from ..models.field import DataType, FieldModel, SourceType
from ..models.schema import ExcelSheetInfo, SourceSchema
from .detector import detect_header_candidates, infer_column_type


class ExcelAnalyzer:
    """
    Analyzes uploaded Excel workbooks dynamically without any hardcoded schemas.
    """

    def __init__(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel file not found at: {file_path}")
        self.file_path = file_path

    def inspect_sheets(self) -> List[ExcelSheetInfo]:
        """Inspect sheet names and visibility without loading all data."""
        wb = openpyxl.load_workbook(self.file_path, read_only=False, data_only=False)
        sheets: List[ExcelSheetInfo] = []
        try:
            for name in wb.sheetnames:
                ws = wb[name]
                is_hidden = ws.sheet_state != "visible"
                candidates = detect_header_candidates(ws, max_scan_rows=20)
                best_row = candidates[0][0] if candidates else 1
                sheets.append(
                    ExcelSheetInfo(
                        name=name,
                        is_hidden=is_hidden,
                        max_row=ws.max_row or 0,
                        max_col=ws.max_column or 0,
                        detected_header_row=best_row,
                        header_candidates=[c[0] for c in candidates[:5]],
                    )
                )
        finally:
            wb.close()
        return sheets

    def analyze_sheet(
        self,
        sheet_name: Optional[str] = None,
        header_row_override: Optional[int] = None,
        max_preview_records: int = 50,
    ) -> SourceSchema:
        """
        Extracts dynamic schema and records from the specified sheet.
        """
        # Load twice: one with data_only=False (to detect formulas), one with data_only=True (to read cached values)
        wb_formulas = openpyxl.load_workbook(self.file_path, data_only=False)
        wb_cached = openpyxl.load_workbook(self.file_path, data_only=True)

        try:
            available_sheets = self.inspect_sheets()
            if not sheet_name:
                # Pick first visible sheet
                visible_sheets = [s.name for s in available_sheets if not s.is_hidden]
                sheet_name = visible_sheets[0] if visible_sheets else wb_formulas.sheetnames[0]

            if sheet_name not in wb_formulas.sheetnames:
                raise ValueError(f"Worksheet '{sheet_name}' not found in workbook.")

            ws_f = wb_formulas[sheet_name]
            ws_c = wb_cached[sheet_name]

            # Detect header row if not overridden
            header_candidates = detect_header_candidates(ws_f, max_scan_rows=25)
            if header_row_override and header_row_override > 0:
                header_row = header_row_override
                header_confidence = 1.0
            else:
                header_row = header_candidates[0][0] if header_candidates else 1
                header_confidence = header_candidates[0][1] if header_candidates else 0.5

            max_row = max(ws_f.max_row or 0, 1)
            max_col = max(ws_f.max_column or 0, 1)

            # Map merged ranges in the worksheet to handle merged header cells
            merged_values: Dict[Tuple[int, int], Any] = {}
            for rng in ws_f.merged_cells.ranges:
                top_left_cell = ws_f.cell(row=rng.min_row, column=rng.min_col)
                val = top_left_cell.value
                for r in range(rng.min_row, rng.max_row + 1):
                    for c in range(rng.min_col, rng.max_col + 1):
                        merged_values[(r, c)] = val

            # Discover headers
            raw_headers: List[Tuple[int, str]] = []
            warnings: List[str] = []
            seen_headers: Dict[str, int] = {}

            for col_idx in range(1, max_col + 1):
                cell_val = ws_f.cell(row=header_row, column=col_idx).value
                if cell_val is None and (header_row, col_idx) in merged_values:
                    cell_val = merged_values[(header_row, col_idx)]

                col_letter = get_column_letter(col_idx)
                if cell_val is None or str(cell_val).strip() == "":
                    # Empty header detected
                    generated_name = f"Column_{col_letter}"
                    warnings.append(f"Column {col_letter} (Index {col_idx}) has an empty header. Named '{generated_name}'.")
                    raw_name = generated_name
                else:
                    raw_name = str(cell_val).strip()

                # Handle duplicates
                lower_name = raw_name.lower()
                if lower_name in seen_headers:
                    seen_headers[lower_name] += 1
                    dedup_name = f"{raw_name}_{seen_headers[lower_name]}"
                    warnings.append(f"Duplicate header '{raw_name}' in column {col_letter} renamed to '{dedup_name}'.")
                    raw_name = dedup_name
                else:
                    seen_headers[lower_name] = 1

                raw_headers.append((col_idx, raw_name))

            # Scan data records from header_row + 1 to max_row
            col_samples: Dict[int, List[Any]] = {col_idx: [] for col_idx, _ in raw_headers}
            col_null_counts: Dict[int, int] = {col_idx: 0 for col_idx, _ in raw_headers}
            all_records: List[Dict[str, Any]] = []
            formula_count = 0
            has_formulas = False

            data_start_row = header_row + 1
            for r_idx in range(data_start_row, max_row + 1):
                row_dict: Dict[str, Any] = {}
                row_has_any_data = False

                for col_idx, h_name in raw_headers:
                    cell_f = ws_f.cell(row=r_idx, column=col_idx)
                    cell_c = ws_c.cell(row=r_idx, column=col_idx)

                    val = cell_c.value if cell_c.value is not None else cell_f.value
                    if val is None and (r_idx, col_idx) in merged_values:
                        val = merged_values[(r_idx, col_idx)]

                    # Check for formulas
                    if cell_f.data_type == "f" or (isinstance(cell_f.value, str) and str(cell_f.value).startswith("=")):
                        has_formulas = True
                        formula_count += 1

                    if val is not None and str(val).strip() != "":
                        row_has_any_data = True
                        col_samples[col_idx].append(val)
                    else:
                        col_null_counts[col_idx] += 1

                    field_id = f"excel_{col_idx}_{re.sub(r'[^a-zA-Z0-9_]', '_', h_name.lower())}"
                    row_dict[field_id] = val

                if row_has_any_data:
                    all_records.append(row_dict)

            if has_formulas:
                warnings.append(f"Detected {formula_count} formulas. Cached calculated values were read; formulas were not executed.")

            # Filter out completely trailing empty columns
            active_fields: List[FieldModel] = []
            for col_idx, h_name in raw_headers:
                samples = col_samples[col_idx]
                col_letter = get_column_letter(col_idx)
                inferred_type = infer_column_type(samples)
                unique_count = len(set(str(s) for s in samples))
                field_id = f"excel_{col_idx}_{re.sub(r'[^a-zA-Z0-9_]', '_', h_name.lower())}"

                field = FieldModel(
                    field_id=field_id,
                    original_name=h_name,
                    normalized_name=re.sub(r"[\s_-]+", "_", h_name.strip().lower()),
                    data_type=inferred_type,
                    source_type=SourceType.EXCEL,
                    location={
                        "sheet": sheet_name,
                        "column_index": col_idx,
                        "column_letter": col_letter,
                        "header_row": header_row,
                        "cell_reference": f"{col_letter}{header_row}",
                    },
                    sample_values=samples[:8],
                    null_count=col_null_counts[col_idx],
                    unique_count=unique_count,
                    confidence=header_confidence,
                    metadata={"total_samples_collected": len(samples)},
                )
                active_fields.append(field)

            preview_records = all_records[:max_preview_records]

            return SourceSchema(
                file_path=self.file_path,
                sheet_name=sheet_name,
                total_rows=len(all_records),
                total_cols=len(active_fields),
                header_row_index=header_row,
                data_start_row=data_start_row,
                fields=active_fields,
                warnings=warnings,
                has_formulas=has_formulas,
                formula_count=formula_count,
                available_sheets=available_sheets,
                preview_records=preview_records,
                all_records=all_records,
            )

        finally:
            wb_formulas.close()
            wb_cached.close()
