"""API service settings — extends the shared :class:`CommonSettings`."""

from __future__ import annotations

from functools import lru_cache

from alphaforge_shared.settings import CommonSettings
from pydantic import Field


class APISettings(CommonSettings):
    # JWT / auth
    jwt_secret_key: str = Field("change-me", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")
    jwt_access_expires: int = Field(3600, alias="JWT_ACCESS_TOKEN_EXPIRES")
    jwt_refresh_expires: int = Field(60 * 60 * 24 * 7, alias="JWT_REFRESH_TOKEN_EXPIRES")

    # OAuth2
    oauth_google_client_id: str = Field("", alias="OAUTH2_GOOGLE_CLIENT_ID")
    oauth_google_client_secret: str = Field("", alias="OAUTH2_GOOGLE_CLIENT_SECRET")
    oauth_github_client_id: str = Field("", alias="OAUTH2_GITHUB_CLIENT_ID")
    oauth_github_client_secret: str = Field("", alias="OAUTH2_GITHUB_CLIENT_SECRET")

    # CORS
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    # Pagination defaults
    page_size_default: int = 50
    page_size_max: int = 500

    # Rate limiting (per IP)
    rate_limit_per_minute: int = 600


@lru_cache(maxsize=1)
def get_settings() -> APISettings:
    return APISettings()
