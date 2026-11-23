"""
Dynamic Word Document Template Analyzer.
Analyzes paragraphs, tables, placeholders, and candidate insertion regions.
"""

import os
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from docx import Document
from docx.table import Table, _Cell

from ..models.field import DataType, FieldModel, SourceType
from ..models.schema import TargetDocumentStructure, TargetSchema, TargetTableInfo
from .ooxml_helper import (
    count_drawings_and_images,
    extract_content_controls,
    is_merged_cell,
)

# Regular expressions for finding placeholders
PLACEHOLDER_PATTERNS = [
    re.compile(r"\{\{([a-zA-Z0-9_\s.-]+)\}\}"),       # {{field}}
    re.compile(r"<<([a-zA-Z0-9_\s.-]+)>>"),           # <<field>>
    re.compile(r"\[([a-zA-Z0-9_\s.-]+)\]"),           # [field]
    re.compile(r"\{([a-zA-Z0-9_.-]+)\}"),             # {field}
    re.compile(r"<([a-zA-Z0-9_.-]+)>"),               # <field>
]


class WordAnalyzer:
    """
    Analyzes Word docx templates dynamically without hardcoded assumptions.
    """

    def __init__(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Word template not found at: {file_path}")
        self.file_path = file_path

    def analyze(self) -> TargetSchema:
        doc = Document(self.file_path)
        warnings: List[str] = []

        total_paragraphs = len(doc.paragraphs)
        total_tables = len(doc.tables)
        total_images = count_drawings_and_images(doc._element)
        total_controls = len(extract_content_controls(doc._element))

        # Check headers and footers
        has_headers_footers = False
        for section in doc.sections:
            if section.header and len(section.header.paragraphs) > 0:
                has_headers_footers = True
            if section.footer and len(section.footer.paragraphs) > 0:
                has_headers_footers = True

        structure = TargetDocumentStructure(
            has_tables=(total_tables > 0),
            table_count=total_tables,
            paragraph_count=total_paragraphs,
            placeholder_count=0,
            has_headers_footers=has_headers_footers,
            sections_count=len(doc.sections),
            unsupported_features_detected=[],
        )

        target_fields: List[FieldModel] = []
        tables_info: List[TargetTableInfo] = []
        candidate_strategies: List[str] = []
        discovered_placeholders: Set[str] = set()

        # 1. Scan paragraphs for placeholders
        for p_idx, p in enumerate(doc.paragraphs):
            text = p.text
            for pattern in PLACEHOLDER_PATTERNS:
                matches = pattern.findall(text)
                for m in matches:
                    clean_m = m.strip()
                    if clean_m and clean_m not in discovered_placeholders:
                        discovered_placeholders.add(clean_m)
                        field_id = f"word_ph_{re.sub(r'[^a-zA-Z0-9_]', '_', clean_m.lower())}"
                        target_fields.append(
                            FieldModel(
                                field_id=field_id,
                                original_name=clean_m,
                                normalized_name=re.sub(r"[\s_-]+", "_", clean_m.lower()),
                                data_type=DataType.STRING,
                                source_type=SourceType.WORD,
                                location={
                                    "type": "paragraph_placeholder",
                                    "paragraph_index": p_idx,
                                    "pattern": pattern.pattern,
                                },
                                sample_values=[clean_m],
                                confidence=0.95,
                                metadata={"context": text[:100]},
                            )
                        )

        # 2. Scan tables
        for t_idx, table in enumerate(doc.tables):
            num_rows = len(table.rows)
            num_cols = len(table.columns) if num_rows > 0 else 0

            has_merged = any(is_merged_cell(cell) for row in table.rows for cell in row.cells)
            is_nested = any(len(cell.tables) > 0 for row in table.rows for cell in row.cells)

            if is_nested:
                warnings.append(f"Table {t_idx + 1} contains nested tables. Nested tables have limited formatting propagation.")
                structure.unsupported_features_detected.append(f"nested_table_in_table_{t_idx + 1}")

            sample_headers: List[str] = []
            header_row_index: Optional[int] = None
            has_repeating_pattern = False
            has_blank_rows = False

            # Header detection in table
            if num_rows > 0:
                first_row_cells = [cell.text.strip() for cell in table.rows[0].cells]
                # If first row has non-empty text in most cells, treat as header row
                non_empty = [c for c in first_row_cells if c]
                if len(non_empty) >= max(1, num_cols // 2):
                    header_row_index = 0
                    sample_headers = first_row_cells

                    # Extract target fields from table headers
                    for col_idx, h_text in enumerate(first_row_cells):
                        name = h_text if h_text else f"Column_{col_idx + 1}"
                        field_id = f"word_table_{t_idx}_col_{col_idx}_{re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())}"
                        target_fields.append(
                            FieldModel(
                                field_id=field_id,
                                original_name=name,
                                normalized_name=re.sub(r"[\s_-]+", "_", name.lower()),
                                data_type=DataType.STRING,
                                source_type=SourceType.WORD,
                                location={
                                    "type": "table_column",
                                    "table_index": t_idx,
                                    "row_index": 0,
                                    "col_index": col_idx,
                                },
                                sample_values=[],
                                confidence=0.9,
                                metadata={"table_index": t_idx, "col_index": col_idx},
                            )
                        )

                # Check for repeating pattern or blank rows
                if num_rows > 1:
                    row1_cells = [cell.text.strip() for cell in table.rows[1].cells]
                    if all(c == "" for c in row1_cells):
                        has_blank_rows = True
                    else:
                        has_repeating_pattern = True

                # Scan table cells for placeholders too
                for r_idx in range(num_rows):
                    for c_idx in range(len(table.rows[r_idx].cells)):
                        cell_text = table.cell(r_idx, c_idx).text
                        for pattern in PLACEHOLDER_PATTERNS:
                            matches = pattern.findall(cell_text)
                            for m in matches:
                                clean_m = m.strip()
                                if clean_m and clean_m not in discovered_placeholders:
                                    discovered_placeholders.add(clean_m)
                                    field_id = f"word_tbl_ph_{t_idx}_{r_idx}_{c_idx}_{re.sub(r'[^a-zA-Z0-9_]', '_', clean_m.lower())}"
                                    target_fields.append(
                                        FieldModel(
                                            field_id=field_id,
                                            original_name=clean_m,
                                            normalized_name=re.sub(r"[\s_-]+", "_", clean_m.lower()),
                                            data_type=DataType.STRING,
                                            source_type=SourceType.WORD,
                                            location={
                                                "type": "table_cell_placeholder",
                                                "table_index": t_idx,
                                                "row_index": r_idx,
                                                "col_index": c_idx,
                                            },
                                            sample_values=[clean_m],
                                            confidence=0.95,
                                            metadata={"table_index": t_idx, "context": cell_text[:80]},
                                        )
                                    )

            # Check if this table looks like a label/value form (e.g. 2 columns: Label / Value)
            is_label_value_form = (num_cols == 2 and num_rows >= 2 and header_row_index is None)

            tables_info.append(
                TargetTableInfo(
                    table_index=t_idx,
                    row_count=num_rows,
                    col_count=num_cols,
                    header_row_index=header_row_index,
                    has_repeating_pattern=has_repeating_pattern,
                    sample_headers=sample_headers,
                    has_merged_cells=has_merged,
                    is_nested=is_nested,
                )
            )

            # Candidate strategies based on table structure
            if has_repeating_pattern:
                candidate_strategies.append("repeat_template_row")
            if has_blank_rows:
                candidate_strategies.append("fill_existing_blank_rows")
            if is_label_value_form:
                candidate_strategies.append("fill_label_value_form")
            candidate_strategies.append("append_rows")

        # Paragraph placeholders strategy
        if discovered_placeholders:
            candidate_strategies.insert(0, "replace_placeholders")

        # Deduplicate strategies preserving order
        unique_strategies: List[str] = []
        for s in candidate_strategies:
            if s not in unique_strategies:
                unique_strategies.append(s)

        if not unique_strategies:
            unique_strategies = ["append_rows"]

        recommended_strategy = unique_strategies[0]
        structure.placeholder_count = len(discovered_placeholders)

        return TargetSchema(
            file_path=self.file_path,
            structure=structure,
            tables=tables_info,
            fields=target_fields,
            candidate_strategies=unique_strategies,
            recommended_strategy=recommended_strategy,
            warnings=warnings,
        )
