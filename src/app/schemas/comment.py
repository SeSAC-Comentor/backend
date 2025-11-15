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
    problem_types: list[str]  # 한글: ["혐오", "성차별", "기타 차별", "욕설/모욕"] 
    confidence: float
    issue_count: int
    reason: str
    all_labels: list[dict]  # 추가: 원본 라벨과 점수

    @classmethod
    def from_classification(cls, classification: dict, reason: str):
        """분류 결과에서 Response DTO 생성"""
        return cls(
            is_problematic=classification["is_problematic"],
            severity=classification["severity"],
            problem_types=classification["problem_types"],
            confidence=classification["confidence"],
            issue_count=classification["issue_count"],
            reason=reason,
            all_labels=classification["all_labels"]  # 추가
        )