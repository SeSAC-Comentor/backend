from fastapi import FastAPI
from app.schemas.comment import (
    CommentRequest,
    CommentReviewResponse,
    CommentCorrectResponse,
    CommentFeedbackResponse,
)

app = FastAPI(
    title="Commento Mock API",
    description="하드코딩된 응답만 제공하는 Mock API입니다.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/")
async def health_check():
    return {"status": "ok"}

@app.post(
    "/api/review",
    response_model=CommentReviewResponse,
    summary="댓글 검토 (빠른 검증)",
    description="댓글에 혐오 표현이 포함되어 있는지 빠르게 검증합니다.",
    responses={
        200: {
            "description": "검증 성공",
            "content": {
                "application/json": {
                    "example": {"is_problematic": True}
                }
            }
        },
        422: {
            "description": "유효성 검사 실패",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "string_type",
                                "loc": ["body", "comment"],
                                "msg": "Input should be a valid string",
                                "input": 123
                            }
                        ]
                    }
                }
            }
        },
        429: {
            "description": "요청 한도 초과",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Too Many Requests",
                        "message": "분당 요청 한도(100개)를 초과했습니다. 잠시 후 다시 시도해주세요."
                    }
                }
            }
        }
    }
)
async def review_comment(request: CommentRequest):
    return CommentReviewResponse(is_problematic=True)

@app.post(
    "/api/correct",
    response_model=CommentCorrectResponse,
    summary="댓글 수정",
    description="혐오 표현을 포함한 댓글을 적절한 표현으로 수정합니다.",
    responses={
        200: {
            "description": "수정 성공",
            "content": {
                "application/json": {
                    "example": {"corrected_comment": "수정된 댓글 텍스트"}
                }
            }
        },
        422: {
            "description": "유효성 검사 실패",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "string_type",
                                "loc": ["body", "comment"],
                                "msg": "Input should be a valid string",
                                "input": 123
                            }
                        ]
                    }
                }
            }
        },
        429: {
            "description": "요청 한도 초과",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Too Many Requests",
                        "message": "분당 요청 한도(100개)를 초과했습니다. 잠시 후 다시 시도해주세요."
                    }
                }
            }
        }
    }
)
async def correct_comment(request: CommentRequest):
    return CommentCorrectResponse(corrected_comment="수정된 댓글 텍스트")

@app.post(
    "/api/feedback",
    response_model=CommentFeedbackResponse,
    summary="상세 피드백",
    description="댓글에 대한 상세한 분석과 개선 사항을 제공합니다.",
    responses={
        200: {
            "description": "피드백 성공",
            "content": {
                "application/json": {
                    "example": {
                        "is_problematic": True,
                        "severity": "높음",
                        "problem_types": ["고정관념", "부적절한 언어"],
                        "confidence": 0.92,
                        "issue_count": 2,
                        "reason": "여성을 특정 직업으로만 한정하는 고정관념이 포함되어 있습니다."
                    }
                }
            }
        },
        422: {
            "description": "유효성 검사 실패",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "string_type",
                                "loc": ["body", "comment"],
                                "msg": "Input should be a valid string",
                                "input": 123
                            }
                        ]
                    }
                }
            }
        },
        429: {
            "description": "요청 한도 초과",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Too Many Requests",
                        "message": "분당 요청 한도(100개)를 초과했습니다. 잠시 후 다시 시도해주세요."
                    }
                }
            }
        }
    }
)
async def feedback_comment(request: CommentRequest):
    return CommentFeedbackResponse(
        is_problematic=True,
        severity="높음",
        problem_types=["고정관념", "부적절한 언어"],
        confidence=0.92,
        issue_count=2,
        reason="여성을 특정 직업으로만 한정하는 고정관념이 포함되어 있습니다."
    )