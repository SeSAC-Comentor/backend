from pydantic import BaseModel, Field

class CommentRequest(BaseModel):
    """모든 엔드포인트에서 사용하는 공통 요청"""
    comment: str = Field(..., min_length=1, max_length=1000)

class CommentReviewResponse(BaseModel):
    """POST /api/review 응답"""
    is_problematic: bool

class CommentCorrectResponse(BaseModel):
    """POST /api/correct 응답"""
    corrected_comment: str

class CommentFeedbackResponse(BaseModel):
    """POST /api/feedback 응답"""
    is_problematic: bool
    severity: str  # "높음", "중간", "낮음"
    problem_types: list[str]  # ["고정관념", "부적절한 언어"]
    confidence: float  # 0.92 같은 신뢰도
    issue_count: int
    reason: str