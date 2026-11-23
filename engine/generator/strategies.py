"""
Document generation insertion strategies.
"""

import copy
import re
from typing import Any, Dict, List, Optional
from docx import Document
from docx.table import Table, _Cell
from docx.text.paragraph import Paragraph

from ..models.mapping import FieldMapping
from ..models.schema import TargetSchema
from .formatter import clone_table_row_with_formatting, preserve_cell_formatting_and_set_text

PLACEHOLDER_REGEXES = [
    (r"\{\{([a-zA-Z0-9_\s.-]+)\}\}", "{{{}}}"),
    (r"<<([a-zA-Z0-9_\s.-]+)>>", "<<{}>>"),
    (r"\[([a-zA-Z0-9_\s.-]+)\]", "[{}]"),
    (r"\{([a-zA-Z0-9_.-]+)\}", "{{{}}}"),
    (r"<([a-zA-Z0-9_.-]+)>", "<{}>"),
]


def replace_placeholders_in_paragraph(paragraph: Paragraph, replacements: Dict[str, str]) -> None:
    """Replaces placeholders in paragraph text while maintaining run formatting."""
    full_text = paragraph.text
    if not full_text:
        return

    modified = False
    new_text = full_text
    for raw_key, val in replacements.items():
        # Match {{raw_key}}, {raw_key}, <<raw_key>>, [raw_key]
        patterns = [
            f"{{{{{raw_key}}}}}",
            f"{{{raw_key}}}",
            f"<<{raw_key}>>",
            f"[{raw_key}]",
            f"<{raw_key}>",
        ]
        for pat in patterns:
            if pat in new_text:
                new_text = new_text.replace(pat, str(val))
                modified = True

    if modified:
        if paragraph.runs:
            paragraph.runs[0].text = new_text
            for r in paragraph.runs[1:]:
                r.text = ""
        else:
            paragraph.text = new_text


def apply_placeholder_replacement(doc: Document, processed_records: List[Dict[str, Any]], mappings: List[FieldMapping]) -> None:
    """
    Replaces all detected placeholders in body paragraphs and table cells.
    If multiple records are provided, uses record 0 for single placeholder document replacement.
    """
    if not processed_records:
        return

    # Build key to value map from record 0
    rec0 = processed_records[0]
    val_map: Dict[str, str] = {}
    for m in mappings:
        val = rec0.get(m.target_field_id, "")
        val_map[m.target_name] = str(val)

    # Paragraphs in body
    for p in doc.paragraphs:
        replace_placeholders_in_paragraph(p, val_map)

    # Tables
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    replace_placeholders_in_paragraph(p, val_map)

    # Headers & footers
    for s in doc.sections:
        if s.header:
            for p in s.header.paragraphs:
                replace_placeholders_in_paragraph(p, val_map)
        if s.footer:
            for p in s.footer.paragraphs:
                replace_placeholders_in_paragraph(p, val_map)


def apply_repeat_template_row(
    table: Table,
    processed_records: List[Dict[str, Any]],
    mappings: List[FieldMapping],
    target_schema: TargetSchema,
    table_index: int = 0,
) -> None:
    """
    Repeats the template data row for each record, preserving exact borders, shading, font sizes.
    """
    if not processed_records:
        return

    num_rows = len(table.rows)
    if num_rows == 0:
        return

    # Determine template row index: row 1 if header is row 0, else row 0
    header_idx = 0
    template_row_idx = 1 if num_rows > 1 else 0

    # Build mapping from column index to target_field_id
    col_to_field: Dict[int, str] = {}
    for f in target_schema.fields:
        loc = f.location
        if loc.get("table_index") == table_index and "col_index" in loc:
            col_to_field[loc["col_index"]] = f.field_id

    # Populate first record into template row
    first_rec = processed_records[0]
    for c_idx, cell in enumerate(table.rows[template_row_idx].cells):
        target_field_id = col_to_field.get(c_idx)
        if target_field_id:
            val = first_rec.get(target_field_id, "")
            preserve_cell_formatting_and_set_text(cell, str(val))

    # Clone template row for subsequent records
    for rec in processed_records[1:]:
        new_row = clone_table_row_with_formatting(table, template_row_idx)
        for c_idx, cell in enumerate(new_row.cells):
            target_field_id = col_to_field.get(c_idx)
            if target_field_id:
                val = rec.get(target_field_id, "")
                preserve_cell_formatting_and_set_text(cell, str(val))


def apply_fill_blank_rows(
    table: Table,
    processed_records: List[Dict[str, Any]],
    mappings: List[FieldMapping],
    target_schema: TargetSchema,
    table_index: int = 0,
) -> None:
    """Fills existing pre-allocated blank rows in table, appending if needed."""
    col_to_field: Dict[int, str] = {}
    for f in target_schema.fields:
        loc = f.location
        if loc.get("table_index") == table_index and "col_index" in loc:
            col_to_field[loc["col_index"]] = f.field_id

    # Identify blank rows (skipping header row 0)
    blank_row_indices = []
    for r_idx in range(1, len(table.rows)):
        if all(c.text.strip() == "" for c in table.rows[r_idx].cells):
            blank_row_indices.append(r_idx)

    rec_idx = 0
    # Fill existing blanks
    for r_idx in blank_row_indices:
        if rec_idx >= len(processed_records):
            break
        rec = processed_records[rec_idx]
        for c_idx, cell in enumerate(table.rows[r_idx].cells):
            target_field_id = col_to_field.get(c_idx)
            if target_field_id:
                val = rec.get(target_field_id, "")
                preserve_cell_formatting_and_set_text(cell, str(val))
        rec_idx += 1

    # If more records remain, clone the last row
    while rec_idx < len(processed_records):
        rec = processed_records[rec_idx]
        new_row = clone_table_row_with_formatting(table, len(table.rows) - 1)
        for c_idx, cell in enumerate(new_row.cells):
            target_field_id = col_to_field.get(c_idx)
            if target_field_id:
                val = rec.get(target_field_id, "")
                preserve_cell_formatting_and_set_text(cell, str(val))
        rec_idx += 1


def apply_label_value_form(
    table: Table,
    processed_records: List[Dict[str, Any]],
    mappings: List[FieldMapping],
) -> None:
    """Populates 2-column key-value forms."""
    if not processed_records:
        return

    rec0 = processed_records[0]
    # Build target_name -> value map
    val_map: Dict[str, str] = {}
    for m in mappings:
        val_map[m.target_name.strip().lower()] = str(rec0.get(m.target_field_id, ""))

    for row in table.rows:
        if len(row.cells) >= 2:
            label_text = row.cells[0].text.strip().lower().rstrip(":")
            if label_text in val_map:
                preserve_cell_formatting_and_set_text(row.cells[1], val_map[label_text])
