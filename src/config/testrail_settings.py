from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class TestRailSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="TESTRAIL_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    base_url: str
    username: str
    api_key: str
    project_id: int


@lru_cache
def get_testrail_settings() -> TestRailSettings:
    return TestRailSettings()
