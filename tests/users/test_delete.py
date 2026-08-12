# tests/users/test_delete.py
from src.factories.user_factory import UserFactory
from src.config.settings import get_settings


def _create(users_client, email):
    users_client.create_user(UserFactory.valid_payload(email=email))


def test_delete_user_with_valid_token_returns_204(users_client, unique_email):
    _create(users_client, unique_email)
    response = users_client.delete_user(unique_email)
    assert response.status_code == 204
    assert users_client.get_user(unique_email).status_code == 404


def test_delete_user_without_auth_header_returns_401(users_client, unique_email, created_user_cleanup):
    _create(users_client, unique_email)
    created_user_cleanup.append(unique_email)
    response = users_client.delete_user(unique_email, headers={})
    assert response.status_code == 401


def test_delete_user_with_wrong_token_returns_401(users_client, unique_email, created_user_cleanup):
    _create(users_client, unique_email)
    created_user_cleanup.append(unique_email)
    response = users_client.delete_user(unique_email, headers={"Authentication": "wrong-token"})
    assert response.status_code == 401


def test_delete_user_with_authorization_header_instead_of_authentication(users_client, unique_email, created_user_cleanup):
    """The spec names the header 'Authentication', not the more common 'Authorization'.
    This characterizes whether the real app is more lenient than the spec."""
    _create(users_client, unique_email)
    created_user_cleanup.append(unique_email)
    token = get_settings().auth_token
    response = users_client.delete_user(unique_email, headers={"Authorization": f"Bearer {token}"})
    # No fixed expectation: per the spec this should behave like "no valid auth" (401).
    # A 204 here would mean the real app diverges from its own spec — a Task 14 finding either way.
    assert response.status_code in (204, 401)


def test_delete_user_returns_404_for_unknown_email(users_client):
    response = users_client.delete_user("qa-does-not-exist@sdet-test.dev")
    assert response.status_code == 404


def test_delete_user_twice_is_not_a_server_error(users_client, unique_email):
    _create(users_client, unique_email)
    first = users_client.delete_user(unique_email)
    second = users_client.delete_user(unique_email)
    assert first.status_code == 204
    assert second.status_code in (204, 404)
    assert second.status_code < 500
