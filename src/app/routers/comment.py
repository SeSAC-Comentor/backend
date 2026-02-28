from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas.comment import (
    CommentRequest,
    CommentReviewResponse,
    CommentCorrectResponse,
    CommentFeedbackResponse,
)
from src.app.services.comment_service import CommentService
from src.app.core.middlewares.rate_limit import limiter
from src.app.auth.dependencies import get_optional_user
from src.app.db.session import get_db
from src.app.models.user import User
from src.app.services.history_service import HistoryService

router = APIRouter(prefix="/api", tags=["comments"])


@router.post(
    "/review",
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
@limiter.limit("100/minute")
async def review_comment(request: Request, body: CommentRequest):
    result = CommentService.classify(body.comment)
    return CommentReviewResponse(is_problematic=result["is_problematic"])


@router.post(
    "/correct",
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
@limiter.limit("100/minute")
async def correct_comment(
    request: Request,
    body: CommentRequest,
    user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    result = await CommentService.correct(body.comment)

    # 인증된 사용자면 히스토리 저장
    if user is not None:
        classification = result.get("classification", {})
        await HistoryService.save(
            db=db,
            user_id=user.id,
            original_comment=body.comment,
            corrected_comment=result["corrected_comment"],
            is_corrected=result["is_corrected"],
            severity=classification.get("severity"),
            confidence=classification.get("confidence"),
            problem_types=classification.get("problem_types"),
            reason=result.get("reason"),
        )

    return CommentCorrectResponse(corrected_comment=result["corrected_comment"])


@router.post(
    "/feedback",
    response_model=CommentFeedbackResponse,
    summary="상세 피드백",
    description="댓글에 대한 상세한 분석과 개선 사항을 제공합니다.",
    responses={
        200: {
            "description": "피드백 성공",
        },
        422: {
            "description": "유효성 검사 실패",
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
@limiter.limit("100/minute")
async def feedback_comment(request: Request, body: CommentRequest):
    return await CommentService.get_feedback(body.comment)
