# audit_engine/common/models.py
from pydantic import BaseModel, Field
from typing import List, Optional

class LineSpan(BaseModel):
    start: int
    end: int

class Finding(BaseModel):
    finding_id: str
    swc_id: str
    severity: str  # Critical, Major, etc.
    tool_name: str
    tool_version: str
    file_path: str
    line_span: LineSpan
    function_name: Optional[str]
    description: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    recommendations: List[str]
    timestamp: Optional[str]
