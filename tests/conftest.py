# tests/conftest.py
import os
import uuid
import pytest
from src.config.settings import get_settings
from src.clients.base_client import BaseClient
from src.clients.users_client import UsersClient

ALL_ENVIRONMENTS = ["dev", "prod"]
TEST_EMAIL_PREFIX = "qa-"


def _active_environments() -> list[str]:
    raw = os.environ.get("TEST_ENVIRONMENTS")
    if not raw:
        return ALL_ENVIRONMENTS
    return [env.strip() for env in raw.split(",") if env.strip()]


def client_for(env: str) -> UsersClient:
    """Public on purpose: Task 12's environment-isolation suite imports this
    directly instead of redefining it, since it needs both dev and prod
    clients regardless of TEST_ENVIRONMENTS filtering."""
    settings = get_settings()
    base = BaseClient(f"{settings.render_base_url}/{env}")
    return UsersClient(base, auth_token=settings.auth_token)


@pytest.fixture(scope="session", autouse=True)
def cleanup_orphaned_test_users():
    for env in ALL_ENVIRONMENTS:
        client = client_for(env)
        response = client.list_users()
        if response.status_code != 200:
            continue
        for user in response.json():
            email = user.get("email", "")
            if email.startswith(TEST_EMAIL_PREFIX):
                client.delete_user(email)
    yield


def pytest_generate_tests(metafunc):
    if "users_client" in metafunc.fixturenames:
        envs = _active_environments()
        metafunc.parametrize("users_client", envs, indirect=True, ids=envs)


@pytest.fixture
def users_client(request):
    return client_for(request.param)


@pytest.fixture
def unique_email():
    return f"{TEST_EMAIL_PREFIX}{uuid.uuid4()}@sdet-test.dev"


@pytest.fixture
def created_user_cleanup(users_client):
    emails_to_cleanup = []
    yield emails_to_cleanup
    for email in emails_to_cleanup:
        users_client.delete_user(email)
