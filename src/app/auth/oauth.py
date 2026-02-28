import httpx

from src.config import config


async def google_exchange_code(code: str) -> dict:
    """Google OAuth code -> access_token + profile."""
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": config.GOOGLE_CLIENT_ID,
                "client_secret": config.GOOGLE_CLIENT_SECRET,
                "redirect_uri": config.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        token_resp.raise_for_status()
        token_data = token_resp.json()

        profile_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        profile_resp.raise_for_status()
        profile = profile_resp.json()

    return {
        "provider": "google",
        "provider_id": profile["id"],
        "nickname": profile.get("name", ""),
        "profile_image": profile.get("picture"),
    }


async def kakao_exchange_code(code: str) -> dict:
    """Kakao OAuth code -> access_token + profile."""
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://kauth.kakao.com/oauth/token",
            data={
                "code": code,
                "client_id": config.KAKAO_CLIENT_ID,
                "client_secret": config.KAKAO_CLIENT_SECRET,
                "redirect_uri": config.KAKAO_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        token_resp.raise_for_status()
        token_data = token_resp.json()

        profile_resp = await client.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        profile_resp.raise_for_status()
        profile = profile_resp.json()

    kakao_account = profile.get("kakao_account", {})
    kakao_profile = kakao_account.get("profile", {})

    return {
        "provider": "kakao",
        "provider_id": str(profile["id"]),
        "nickname": kakao_profile.get("nickname", ""),
        "profile_image": kakao_profile.get("profile_image_url"),
    }
