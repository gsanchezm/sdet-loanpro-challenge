from src.config.settings import get_settings

def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("SDET_RENDER_BASE_URL", "https://example.onrender.com")
    monkeypatch.setenv("SDET_AUTH_TOKEN", "mysecrettoken")
    get_settings.cache_clear()
    try:
        settings = get_settings()
        assert settings.render_base_url == "https://example.onrender.com"
        assert settings.auth_token == "mysecrettoken"
    finally:
        # Drop the cached fake settings so later tests that call
        # get_settings() (e.g. via conftest's users_client fixture) resolve
        # the real .env values instead of this test's monkeypatched ones.
        get_settings.cache_clear()
