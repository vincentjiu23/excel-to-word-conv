"""
Conversion session models.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from .schema import SourceSchema, TargetSchema
from .mapping import FieldMapping


class SessionStatus(str):
    INITIALIZED = "initialized"
    EXCEL_ANALYZED = "excel_analyzed"
    WORD_ANALYZED = "word_analyzed"
    MAPPED = "mapped"
    CONVERTED = "converted"
    FAILED = "failed"


class ConversionSession(BaseModel):
    session_id: str
    excel_path: Optional[str] = None
    word_path: Optional[str] = None
    output_path: Optional[str] = None
    selected_sheet: Optional[str] = None
    header_row_override: Optional[int] = None
    selected_table_index: Optional[int] = None
    insertion_strategy: Optional[str] = "repeat_template_row"
    source_schema: Optional[SourceSchema] = None
    target_schema: Optional[TargetSchema] = None
    mappings: List[FieldMapping] = Field(default_factory=list)
    selected_record_indices: List[int] = Field(default_factory=list)
    status: str = SessionStatus.INITIALIZED
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    error_message: Optional[str] = None
    conversion_summary: Dict[str, Any] = Field(default_factory=dict)
