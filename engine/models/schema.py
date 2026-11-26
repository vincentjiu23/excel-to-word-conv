"""
Schema models for Excel source and Word target.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .field import FieldModel


class ExcelSheetInfo(BaseModel):
    name: str
    is_hidden: bool = False
    max_row: int = 0
    max_col: int = 0
    detected_header_row: Optional[int] = None
    header_candidates: List[int] = Field(default_factory=list)


class SourceSchema(BaseModel):
    """
    Dynamically extracted schema from an Excel worksheet.
    """
    file_path: str
    sheet_name: str
    total_rows: int
    total_cols: int
    header_row_index: int
    data_start_row: int
    fields: List[FieldModel]
    warnings: List[str] = Field(default_factory=list)
    has_formulas: bool = False
    formula_count: int = 0
    available_sheets: List[ExcelSheetInfo] = Field(default_factory=list)
    preview_records: List[Dict[str, Any]] = Field(default_factory=list)
    all_records: List[Dict[str, Any]] = Field(default_factory=list, exclude=True)


class TargetDocumentStructure(BaseModel):
    has_tables: bool = False
    table_count: int = 0
    paragraph_count: int = 0
    placeholder_count: int = 0
    has_headers_footers: bool = False
    sections_count: int = 1
    unsupported_features_detected: List[str] = Field(default_factory=list)


class TargetTableInfo(BaseModel):
    table_index: int
    row_count: int
    col_count: int
    header_row_index: Optional[int] = None
    has_repeating_pattern: bool = False
    sample_headers: List[str] = Field(default_factory=list)
    has_merged_cells: bool = False
    is_nested: bool = False


class TargetSchema(BaseModel):
    """
    Dynamically extracted target schema from Word template.
    """
    file_path: str
    structure: TargetDocumentStructure
    tables: List[TargetTableInfo] = Field(default_factory=list)
    fields: List[FieldModel] = Field(default_factory=list)
    candidate_strategies: List[str] = Field(default_factory=list)
    recommended_strategy: str = "repeat_template_row"
    warnings: List[str] = Field(default_factory=list)
