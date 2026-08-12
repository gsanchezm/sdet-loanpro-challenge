from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SDET_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    render_base_url: str
    auth_token: str

@lru_cache
def get_settings() -> Settings:
    return Settings()
