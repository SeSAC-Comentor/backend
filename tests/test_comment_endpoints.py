from unittest.mock import patch, AsyncMock, MagicMock

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.user import User
from src.app.services.history_service import HistoryService
from tests.conftest import make_problematic_classifier_mock


async def test_health_check(client: AsyncClient):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


async def test_review_non_problematic(client: AsyncClient):
    """문제 없는 댓글 검토."""
    resp = await client.post("/api/review", json={"comment": "좋은 댓글입니다"})

    assert resp.status_code == 200
    data = resp.json()
    assert "is_problematic" in data


async def test_review_empty_comment(client: AsyncClient):
    """빈 댓글은 422."""
    resp = await client.post("/api/review", json={"comment": ""})
    assert resp.status_code == 422


async def test_correct_non_problematic(client: AsyncClient):
    """문제 없는 댓글 교정 — 원본 반환."""
    resp = await client.post("/api/correct", json={"comment": "좋은 댓글입니다"})

    assert resp.status_code == 200
    data = resp.json()
    assert "corrected_comment" in data


async def test_correct_problematic(client: AsyncClient):
    """문제 있는 댓글 교정."""
    mock = make_problematic_classifier_mock()
    with patch("src.app.services.comment_service.classifier_instance", mock), \
         patch("src.app.services.comment_service.correct_comment_text", new_callable=AsyncMock, return_value="수정된 댓글"):
        resp = await client.post("/api/correct", json={"comment": "나쁜 댓글"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["corrected_comment"] == "수정된 댓글"


async def test_feedback_non_problematic(client: AsyncClient):
    """문제 없는 댓글 피드백."""
    resp = await client.post("/api/feedback", json={"comment": "좋은 댓글입니다"})

    assert resp.status_code == 200
    data = resp.json()
    assert "is_problematic" in data
    assert "severity" in data
    assert "reason" in data


async def test_correct_with_auth_saves_history(
    client: AsyncClient, test_user: User, auth_headers: dict, db_session: AsyncSession
):
    """인증된 사용자의 교정 결과가 히스토리에 저장됨."""
    resp = await client.post("/api/correct", json={"comment": "좋은 댓글"}, headers=auth_headers)
    assert resp.status_code == 200

    items, total = await HistoryService.list_by_user(db_session, test_user.id)
    assert total == 1
    assert items[0].original_comment == "좋은 댓글"


async def test_correct_without_auth_no_history(client: AsyncClient, db_session: AsyncSession, test_user: User):
    """비인증 교정은 히스토리에 저장되지 않음."""
    resp = await client.post("/api/correct", json={"comment": "좋은 댓글"})
    assert resp.status_code == 200

    items, total = await HistoryService.list_by_user(db_session, test_user.id)
    assert total == 0
