"""
Generic Field Model and Registry
Non-negotiable principle: The uploaded files define the schema.
No hardcoded business parameters or column names.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DataType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    DATE = "date"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    UNKNOWN = "unknown"


class SourceType(str, Enum):
    EXCEL = "excel"
    WORD = "word"
    PDF = "pdf"


class FieldModel(BaseModel):
    """
    Schema-independent generic field representation.
    """
    field_id: str = Field(..., description="Unique generated identifier for field")
    original_name: str = Field(..., description="Original raw detected field name/label")
    normalized_name: str = Field(..., description="Cleaned, lowercase, normalized name")
    data_type: DataType = Field(default=DataType.UNKNOWN, description="Inferred or declared data type")
    source_type: SourceType = Field(..., description="Origin of field: excel or word")
    location: Dict[str, Any] = Field(default_factory=dict, description="Positional metadata in document")
    sample_values: List[Any] = Field(default_factory=list, description="Extracted non-empty sample values")
    null_count: int = Field(default=0, description="Number of null or blank occurrences")
    unique_count: int = Field(default=0, description="Count of distinct sample values")
    confidence: float = Field(default=1.0, description="Header / field detection confidence (0.0 to 1.0)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary engine or format metadata")

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
