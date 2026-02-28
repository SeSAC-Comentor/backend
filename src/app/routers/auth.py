import hashlib
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.session import get_db
from src.app.models.user import User
from src.app.auth.jwt import create_access_token, create_refresh_token, decode_token
from src.app.auth.dependencies import get_current_user
from src.app.auth.oauth import google_exchange_code, kakao_exchange_code
from src.app.schemas.auth import OAuthCodeRequest, TokenResponse, RefreshTokenRequest, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def _get_or_create_user(db: AsyncSession, profile: dict) -> User:
    """provider+provider_id로 조회, 없으면 생성."""
    result = await db.execute(
        select(User).where(
            User.provider == profile["provider"],
            User.provider_id == profile["provider_id"],
        )
    )
    user = result.scalar_one_or_none()
    if user is None:
        user = User(
            nickname=profile["nickname"],
            profile_image=profile.get("profile_image"),
            provider=profile["provider"],
            provider_id=profile["provider_id"],
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


async def _issue_tokens(db: AsyncSession, user: User) -> TokenResponse:
    """토큰 발급 + refresh_token 해시 저장."""
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    user.refresh_token = _hash_token(refresh_token)
    await db.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


# --- Google OAuth ---

@router.post("/google", response_model=TokenResponse, summary="Google 소셜 로그인")
async def google_login(body: OAuthCodeRequest, db: AsyncSession = Depends(get_db)):
    """Extension에서 받은 Google authorization code로 로그인/회원가입."""
    try:
        profile = await google_exchange_code(body.code)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google 인증 실패")

    user = await _get_or_create_user(db, profile)
    return await _issue_tokens(db, user)


# --- Kakao OAuth ---

@router.post("/kakao", response_model=TokenResponse, summary="Kakao 소셜 로그인")
async def kakao_login(body: OAuthCodeRequest, db: AsyncSession = Depends(get_db)):
    """Extension에서 받은 Kakao authorization code로 로그인/회원가입."""
    try:
        profile = await kakao_exchange_code(body.code)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kakao 인증 실패")

    user = await _get_or_create_user(db, profile)
    return await _issue_tokens(db, user)


# --- Token refresh ---

@router.post("/refresh", response_model=TokenResponse, summary="토큰 갱신")
async def refresh_token(body: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(body.refresh_token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 리프레시 토큰입니다.")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="리프레시 토큰이 아닙니다.")

    user_id = uuid.UUID(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="사용자를 찾을 수 없습니다.")

    if user.refresh_token != _hash_token(body.refresh_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="리프레시 토큰이 일치하지 않습니다.")

    return await _issue_tokens(db, user)


# --- User info ---

@router.get("/me", response_model=UserResponse, summary="현재 사용자 정보")
async def get_me(user: User = Depends(get_current_user)):
    return user
