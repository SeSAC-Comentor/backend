import uuid
from unittest.mock import patch, AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.app.db.base import Base
from src.app.models.user import User
from src.app.models.correction_history import CorrectionHistory  # noqa: F401 — 테이블 등록용
from src.app.auth.jwt import create_access_token


@pytest.fixture
async def db_engine():
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest.fixture
async def client(db_engine):
    """ML 모델을 mock하고 테스트 DB를 주입한 AsyncClient."""
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    # classifier mock — 모델 로딩 방지
    mock_classifier = MagicMock()
    mock_classifier.predict.return_value = [[
        {"label": "hate", "score": 0.05},
        {"label": "offensive", "score": 0.03},
        {"label": "bias_gender", "score": 0.02},
        {"label": "bias_others", "score": 0.01},
    ]]

    with patch("src.app.models.classifier.HateSpeechClassifier", return_value=mock_classifier), \
         patch("src.app.models.classifier.classifier_instance", mock_classifier), \
         patch("src.app.services.comment_service.classifier_instance", mock_classifier):

        from src.app.db import session as session_module
        from src.main import app

        # DB 의존성 오버라이드
        async def override_get_db():
            async with session_factory() as session:
                yield session

        app.dependency_overrides[session_module.get_db] = override_get_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

        app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """테스트용 유저 생성."""
    user = User(
        nickname="테스트유저",
        provider="google",
        provider_id="google-123",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """인증 헤더."""
    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}


def make_problematic_classifier_mock():
    """문제 있는 댓글로 분류하는 mock."""
    mock = MagicMock()
    mock.predict.return_value = [[
        {"label": "hate", "score": 0.85},
        {"label": "offensive", "score": 0.72},
        {"label": "bias_gender", "score": 0.15},
        {"label": "bias_others", "score": 0.05},
    ]]
    return mock
