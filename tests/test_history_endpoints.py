import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.user import User
from src.app.services.history_service import HistoryService


async def test_list_history_requires_auth(client: AsyncClient):
    """인증 없으면 401."""
    resp = await client.get("/api/history")
    assert resp.status_code == 401


async def test_list_history(client: AsyncClient, test_user: User, auth_headers: dict, db_session: AsyncSession):
    """인증된 사용자의 히스토리 목록 조회."""
    for i in range(3):
        await HistoryService.save(
            db=db_session,
            user_id=test_user.id,
            original_comment=f"댓글 {i}",
            corrected_comment=f"수정 {i}",
            is_corrected=True,
            severity="높음",
            confidence=0.85,
            problem_types=["혐오"],
        )

    resp = await client.get("/api/history", headers=auth_headers)

    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    assert data["page"] == 1
    assert data["size"] == 20


async def test_list_history_pagination(client: AsyncClient, test_user: User, auth_headers: dict, db_session: AsyncSession):
    """페이지네이션 파라미터."""
    for i in range(5):
        await HistoryService.save(
            db=db_session,
            user_id=test_user.id,
            original_comment=f"댓글 {i}",
            corrected_comment=f"수정 {i}",
            is_corrected=True,
        )

    resp = await client.get("/api/history?page=1&size=2", headers=auth_headers)

    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["size"] == 2


async def test_get_history_detail(client: AsyncClient, test_user: User, auth_headers: dict, db_session: AsyncSession):
    """히스토리 상세 조회."""
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

    resp = await client.get(f"/api/history/{history.id}", headers=auth_headers)

    assert resp.status_code == 200
    data = resp.json()
    assert data["original_comment"] == "원본 댓글"
    assert data["corrected_comment"] == "수정 댓글"
    assert data["reason"] == "혐오 표현 감지"


async def test_get_history_detail_requires_auth(client: AsyncClient):
    """상세 조회 인증 없으면 401."""
    resp = await client.get(f"/api/history/{uuid.uuid4()}")
    assert resp.status_code == 401


async def test_get_history_detail_not_found(client: AsyncClient, auth_headers: dict):
    """존재하지 않는 히스토리 상세 조회 시 404."""
    resp = await client.get(f"/api/history/{uuid.uuid4()}", headers=auth_headers)
    assert resp.status_code == 404


async def test_delete_history(client: AsyncClient, test_user: User, auth_headers: dict, db_session: AsyncSession):
    """히스토리 삭제."""
    history = await HistoryService.save(
        db=db_session,
        user_id=test_user.id,
        original_comment="삭제 대상",
        corrected_comment="수정",
        is_corrected=True,
    )

    resp = await client.delete(f"/api/history/{history.id}", headers=auth_headers)
    assert resp.status_code == 204


async def test_delete_history_requires_auth(client: AsyncClient):
    """인증 없이 삭제 시 401."""
    resp = await client.delete(f"/api/history/{uuid.uuid4()}")
    assert resp.status_code == 401


async def test_delete_nonexistent_history(client: AsyncClient, auth_headers: dict):
    """존재하지 않는 히스토리 삭제 시 404."""
    resp = await client.delete(f"/api/history/{uuid.uuid4()}", headers=auth_headers)
    assert resp.status_code == 404
