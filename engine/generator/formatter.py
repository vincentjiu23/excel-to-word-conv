"""
Formatting preservation helpers for Word document generation.
"""

from typing import Any, Dict, List, Optional
from docx.table import Table, _Cell, _Row
from docx.text.paragraph import Paragraph
from docx.text.run import Run
from ..word.ooxml_helper import clone_element


def preserve_cell_formatting_and_set_text(cell: _Cell, text: str) -> None:
    """
    Sets text in a cell while preserving paragraph and run formatting (fonts, styles, sizes, bold).
    """
    if not cell.paragraphs:
        cell.add_paragraph(text)
        return

    first_p = cell.paragraphs[0]
    if first_p.runs:
        # Keep formatting of the first run
        target_run = first_p.runs[0]
        target_run.text = text
        # Remove subsequent runs in this paragraph
        for r in first_p.runs[1:]:
            r.text = ""
    else:
        first_p.text = text

    # Clear any extra paragraphs in the cell
    for extra_p in cell.paragraphs[1:]:
        extra_p.text = ""


def clone_table_row_with_formatting(table: Table, source_row_idx: int) -> _Row:
    """
    Deep-clones a row element and appends it to the table, preserving full XML styling.
    """
    src_row = table.rows[source_row_idx]
    cloned_tr = clone_element(src_row._tr)
    table._tbl.append(cloned_tr)
    # The new row is now the last row in table.rows
    return table.rows[-1]
