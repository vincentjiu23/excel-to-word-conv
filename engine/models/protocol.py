"""
Versioned JSON IPC Protocol between Desktop Backend and Python Engine.
Protocol Version: 1.0.0
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

PROTOCOL_VERSION = "1.0.0"


class IPCRequest(BaseModel):
    command: str
    request_id: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    protocol_version: str = PROTOCOL_VERSION


class IPCResponse(BaseModel):
    success: bool
    request_id: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    warnings: list[str] = Field(default_factory=list)
    protocol_version: str = PROTOCOL_VERSION
