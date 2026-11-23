"""
OOXML helper utilities for Word document inspection and manipulation.
"""

import copy
import re
from typing import Any, Dict, List, Optional
from docx.oxml import OxmlElement
from docx.oxml.ns import qn, nsdecls
from docx.table import _Cell, Table


def clone_element(element):
    """Deep clone an oxml element."""
    return copy.deepcopy(element)


def has_shading(cell: _Cell) -> bool:
    """Check if cell has background shading."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = tcPr.find(qn("w:shd"))
    return shd is not None


def get_cell_shading_color(cell: _Cell) -> Optional[str]:
    """Get fill color hex of cell shading if present."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = tcPr.find(qn("w:shd"))
    if shd is not None:
        return shd.get(qn("w:fill"))
    return None


def is_merged_cell(cell: _Cell) -> bool:
    """Detect if cell has horizontal or vertical merge attributes."""
    tcPr = cell._tc.get_or_add_tcPr()
    gridSpan = tcPr.find(qn("w:gridSpan"))
    vMerge = tcPr.find(qn("w:vMerge"))
    return gridSpan is not None or vMerge is not None


def extract_content_controls(docx_element) -> List[Dict[str, str]]:
    """Find any Word Content Controls (sdt) within element."""
    sdt_elements = docx_element.findall(".//" + qn("w:sdt"))
    controls: List[Dict[str, str]] = []
    for sdt in sdt_elements:
        tag = sdt.find(".//" + qn("w:tag"))
        alias = sdt.find(".//" + qn("w:alias"))
        controls.append(
            {
                "tag": tag.get(qn("w:val")) if tag is not None else "",
                "alias": alias.get(qn("w:val")) if alias is not None else "",
            }
        )
    return controls


def count_drawings_and_images(docx_element) -> int:
    """Count image and drawing tags in element."""
    drawings = docx_element.findall(".//" + qn("w:drawing"))
    pictures = docx_element.findall(".//" + qn("w:pict"))
    return len(drawings) + len(pictures)
