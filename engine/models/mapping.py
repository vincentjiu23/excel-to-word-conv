"""
Mapping models and statuses.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MappingStatus(str, Enum):
    EXACT_MATCH = "exact_match"
    RECOMMENDED = "recommended"
    HIGH_CONFIDENCE = "high_confidence"
    NEEDS_REVIEW = "needs_review"
    AMBIGUOUS = "ambiguous"
    UNMATCHED = "unmatched"
    IGNORED = "ignored"
    MANUALLY_ASSIGNED = "manually_assigned"


class FieldTransformation(BaseModel):
    transform_type: str = Field(..., description="e.g. trim, uppercase, lowercase, titlecase, date_format, number_format, default_value, prefix, suffix")
    parameters: Dict[str, Any] = Field(default_factory=dict)


class FieldMapping(BaseModel):
    mapping_id: str
    target_field_id: str
    target_name: str
    source_field_id: Optional[str] = None
    source_name: Optional[str] = None
    confidence: float = 0.0
    status: MappingStatus = MappingStatus.UNMATCHED
    reason: str = "No match detected"
    stage: str = "initial"
    transformations: List[FieldTransformation] = Field(default_factory=list)
    constant_value: Optional[Any] = None
    default_value: Optional[Any] = None
    user_override: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
