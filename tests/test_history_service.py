import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.user import User
from src.app.services.history_service import HistoryService


async def test_save_history(db_session: AsyncSession, test_user: User):
    """히스토리 저장."""
    history = await HistoryService.save(
        db=db_session,
        user_id=test_user.id,
        original_comment="나쁜 댓글",
        corrected_comment="좋은 댓글",
        is_corrected=True,
        severity="높음",
        confidence=0.85,
        problem_types=["혐오", "욕설/모욕"],
        reason="혐오 표현이 감지됨",
    )

    assert history.id is not None
    assert history.user_id == test_user.id
    assert history.original_comment == "나쁜 댓글"
    assert history.corrected_comment == "좋은 댓글"
    assert history.is_corrected is True
    assert history.severity == "높음"


async def test_list_by_user(db_session: AsyncSession, test_user: User):
    """유저별 히스토리 조회."""
    for i in range(5):
        await HistoryService.save(
            db=db_session,
            user_id=test_user.id,
            original_comment=f"댓글 {i}",
            corrected_comment=f"수정 {i}",
            is_corrected=True,
        )

    items, total = await HistoryService.list_by_user(db_session, test_user.id)

    assert total == 5
    assert len(items) == 5
    # 최신순 정렬 확인
    assert items[0].original_comment == "댓글 4"


async def test_list_pagination(db_session: AsyncSession, test_user: User):
    """페이지네이션."""
    for i in range(15):
        await HistoryService.save(
            db=db_session,
            user_id=test_user.id,
            original_comment=f"댓글 {i}",
            corrected_comment=f"수정 {i}",
            is_corrected=True,
        )

    items_p1, total = await HistoryService.list_by_user(db_session, test_user.id, page=1, size=10)
    items_p2, _ = await HistoryService.list_by_user(db_session, test_user.id, page=2, size=10)

    assert total == 15
    assert len(items_p1) == 10
    assert len(items_p2) == 5


async def test_get_by_id(db_session: AsyncSession, test_user: User):
    """ID로 히스토리 상세 조회."""
    history = await HistoryService.save(
        db=db_session,
        user_id=test_user.id,
        original_comment="원본 댓글",
        corrected_comment="수정 댓글",
        is_corrected=True,
        severity="높음",
        confidence=0.85,
        problem_types=["혐오"],
        reason="혐오 표현 감지",
    )

    result = await HistoryService.get_by_id(db_session, history.id, test_user.id)
    assert result is not None
    assert result.id == history.id
    assert result.original_comment == "원본 댓글"
    assert result.reason == "혐오 표현 감지"


async def test_get_by_id_other_user(db_session: AsyncSession, test_user: User):
    """타인의 히스토리는 조회 불가."""
    history = await HistoryService.save(
        db=db_session,
        user_id=test_user.id,
        original_comment="내 댓글",
        corrected_comment="수정",
        is_corrected=True,
    )

    result = await HistoryService.get_by_id(db_session, history.id, uuid.uuid4())
    assert result is None


async def test_delete_history(db_session: AsyncSession, test_user: User):
    """히스토리 삭제."""
    history = await HistoryService.save(
        db=db_session,
        user_id=test_user.id,
        original_comment="삭제할 댓글",
        corrected_comment="삭제할 수정",
        is_corrected=True,
    )

    deleted = await HistoryService.delete_by_id(db_session, history.id, test_user.id)
    assert deleted is True

    items, total = await HistoryService.list_by_user(db_session, test_user.id)
    assert total == 0


async def test_delete_other_users_history(db_session: AsyncSession, test_user: User):
    """타인의 히스토리는 삭제 불가."""
    history = await HistoryService.save(
        db=db_session,
        user_id=test_user.id,
        original_comment="타인 댓글",
        corrected_comment="타인 수정",
        is_corrected=True,
    )

    other_user_id = uuid.uuid4()
    deleted = await HistoryService.delete_by_id(db_session, history.id, other_user_id)
    assert deleted is False

    # 원본은 그대로 존재
    items, total = await HistoryService.list_by_user(db_session, test_user.id)
    assert total == 1


async def test_list_only_own_history(db_session: AsyncSession, test_user: User):
    """다른 유저의 히스토리는 조회 안 됨."""
    await HistoryService.save(
        db=db_session,
        user_id=test_user.id,
        original_comment="내 댓글",
        corrected_comment="내 수정",
        is_corrected=True,
    )

    other_user_id = uuid.uuid4()
    items, total = await HistoryService.list_by_user(db_session, other_user_id)
    assert total == 0
    assert len(items) == 0
