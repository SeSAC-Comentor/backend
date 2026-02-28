import uuid
from datetime import datetime

from pydantic import BaseModel


class HistoryResponse(BaseModel):
    id: uuid.UUID
    original_comment: str
    corrected_comment: str
    is_corrected: bool
    severity: str | None
    confidence: float | None
    problem_types: list[str] | None
    reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class HistoryListResponse(BaseModel):
    items: list[HistoryResponse]
    total: int
    page: int
    size: int
