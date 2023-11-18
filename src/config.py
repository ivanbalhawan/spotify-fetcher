import uuid

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    spotipy_cache: str = ".spotipyoauthcache"
    spotipy_client_id: str = Field(..., exclude=True)
    spotipy_client_secret: str = Field(..., exclude=True)
    spotipy_scope: str = "user-library-read"
    spotipy_state: int = uuid.getnode()


class BackendSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    server_address: str = "http://localhost"
    port_number: int = 56626


auth_settings = AuthSettings()
backend_settings = BackendSettings()


__all__ = ["auth_settings", "backend_settings"]
