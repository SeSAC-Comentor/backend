import uuid
import time
from unittest.mock import patch

import jwt as pyjwt
import pytest

from src.app.auth.jwt import create_access_token, create_refresh_token, decode_token
from src.config import config


def test_access_token_creation():
    user_id = uuid.uuid4()
    token = create_access_token(user_id)
    payload = decode_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "iat" in payload


def test_refresh_token_creation():
    user_id = uuid.uuid4()
    token = create_refresh_token(user_id)
    payload = decode_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["type"] == "refresh"
    assert "exp" in payload


def test_access_token_expiry():
    user_id = uuid.uuid4()
    with patch.object(config, "JWT_ACCESS_TOKEN_EXPIRE_MINUTES", -1):
        token = create_access_token(user_id)

    with pytest.raises(pyjwt.ExpiredSignatureError):
        decode_token(token)


def test_refresh_token_expiry():
    user_id = uuid.uuid4()
    with patch.object(config, "JWT_REFRESH_TOKEN_EXPIRE_DAYS", -1):
        token = create_refresh_token(user_id)

    with pytest.raises(pyjwt.ExpiredSignatureError):
        decode_token(token)


def test_invalid_token():
    with pytest.raises(pyjwt.DecodeError):
        decode_token("invalid-token-string")


@pytest.mark.filterwarnings("ignore::jwt.warnings.InsecureKeyLengthWarning")
def test_wrong_secret():
    user_id = uuid.uuid4()
    token = create_access_token(user_id)

    with pytest.raises(pyjwt.InvalidSignatureError):
        pyjwt.decode(token, "wrong-secret", algorithms=[config.JWT_ALGORITHM])


def test_different_token_types():
    """access token과 refresh token은 다른 type 필드를 가져야 한다."""
    user_id = uuid.uuid4()
    access = create_access_token(user_id)
    refresh = create_refresh_token(user_id)

    assert decode_token(access)["type"] == "access"
    assert decode_token(refresh)["type"] == "refresh"
