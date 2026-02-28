import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.auth.dependencies import get_current_user
from src.app.db.session import get_db
from src.app.models.user import User
from src.app.schemas.history import HistoryResponse, HistoryListResponse
from src.app.services.history_service import HistoryService

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=HistoryListResponse, summary="교정 히스토리 목록")
async def list_history(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await HistoryService.list_by_user(db, user.id, page, size)
    return HistoryListResponse(
        items=[HistoryResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/{history_id}", response_model=HistoryResponse, summary="히스토리 상세 조회")
async def get_history(
    history_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    history = await HistoryService.get_by_id(db, history_id, user.id)
    if history is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="히스토리를 찾을 수 없습니다.")
    return history


@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT, summary="히스토리 삭제")
async def delete_history(
    history_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await HistoryService.delete_by_id(db, history_id, user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="히스토리를 찾을 수 없습니다.")
