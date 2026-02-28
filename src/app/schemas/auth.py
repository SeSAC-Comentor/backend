import uuid
from datetime import datetime

from pydantic import BaseModel


class OAuthCodeRequest(BaseModel):
    code: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: uuid.UUID
    nickname: str
    profile_image: str | None
    provider: str
    created_at: datetime

    model_config = {"from_attributes": True}
