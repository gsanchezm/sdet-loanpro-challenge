from src.config.settings import get_settings

def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("SDET_RENDER_BASE_URL", "https://example.onrender.com")
    monkeypatch.setenv("SDET_AUTH_TOKEN", "mysecrettoken")
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.render_base_url == "https://example.onrender.com"
    assert settings.auth_token == "mysecrettoken"
