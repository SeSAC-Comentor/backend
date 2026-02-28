import hashlib
import uuid
from unittest.mock import patch, AsyncMock

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.auth.jwt import create_access_token, create_refresh_token
from src.app.models.user import User


async def test_google_login_creates_user(client: AsyncClient):
    """Google 소셜 로그인으로 신규 유저 생성 + 토큰 발급."""
    mock_profile = {
        "provider": "google",
        "provider_id": "google-new-456",
        "nickname": "New User",
        "profile_image": "https://example.com/photo.jpg",
    }
    with patch("src.app.routers.auth.google_exchange_code", new_callable=AsyncMock, return_value=mock_profile):
        resp = await client.post("/api/auth/google", json={"code": "test-code"})

    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_google_login_existing_user(client: AsyncClient, test_user: User):
    """기존 유저면 새로 생성하지 않고 토큰만 발급."""
    mock_profile = {
        "provider": test_user.provider,
        "provider_id": test_user.provider_id,
        "nickname": test_user.nickname,
        "profile_image": None,
    }
    with patch("src.app.routers.auth.google_exchange_code", new_callable=AsyncMock, return_value=mock_profile):
        resp = await client.post("/api/auth/google", json={"code": "test-code"})

    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data


async def test_kakao_login_creates_user(client: AsyncClient):
    """Kakao 소셜 로그인으로 신규 유저 생성 + 토큰 발급."""
    mock_profile = {
        "provider": "kakao",
        "provider_id": "kakao-789",
        "nickname": "카카오유저",
        "profile_image": None,
    }
    with patch("src.app.routers.auth.kakao_exchange_code", new_callable=AsyncMock, return_value=mock_profile):
        resp = await client.post("/api/auth/kakao", json={"code": "test-code"})

    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


async def test_google_login_failure(client: AsyncClient):
    """OAuth 코드 교환 실패 시 400 에러."""
    with patch("src.app.routers.auth.google_exchange_code", new_callable=AsyncMock, side_effect=Exception("fail")):
        resp = await client.post("/api/auth/google", json={"code": "bad-code"})

    assert resp.status_code == 400


async def test_refresh_token_endpoint(client: AsyncClient, test_user: User, db_session: AsyncSession):
    """리프레시 토큰으로 새 토큰 쌍 발급."""
    refresh = create_refresh_token(test_user.id)
    test_user.refresh_token = hashlib.sha256(refresh.encode()).hexdigest()
    await db_session.commit()

    resp = await client.post("/api/auth/refresh", json={"refresh_token": refresh})

    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_refresh_with_invalid_token(client: AsyncClient):
    """잘못된 리프레시 토큰은 401."""
    resp = await client.post("/api/auth/refresh", json={"refresh_token": "invalid"})
    assert resp.status_code == 401


async def test_refresh_with_access_token(client: AsyncClient, test_user: User):
    """액세스 토큰을 리프레시에 사용하면 401."""
    access = create_access_token(test_user.id)
    resp = await client.post("/api/auth/refresh", json={"refresh_token": access})
    assert resp.status_code == 401


async def test_me_endpoint(client: AsyncClient, test_user: User, auth_headers: dict):
    """/me 엔드포인트에서 현재 유저 정보 반환."""
    resp = await client.get("/api/auth/me", headers=auth_headers)

    assert resp.status_code == 200
    data = resp.json()
    assert data["nickname"] == test_user.nickname
    assert data["provider"] == test_user.provider
    assert "id" in data


async def test_me_without_auth(client: AsyncClient):
    """인증 없으면 401."""
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 401
