import pytest
from src.factories.user_factory import UserFactory
from src.models.user import User


def test_list_users_returns_200_and_array(users_client):
    response = users_client.list_users()
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    for item in response.json():
        User.model_validate(item)


def test_list_users_contains_a_freshly_created_user(users_client, unique_email, created_user_cleanup):
    payload = UserFactory.valid_payload(email=unique_email)
    users_client.create_user(payload)
    created_user_cleanup.append(unique_email)

    emails = [u["email"] for u in users_client.list_users().json()]
    assert unique_email in emails


def test_get_user_by_email_returns_200(users_client, unique_email, created_user_cleanup):
    payload = UserFactory.valid_payload(email=unique_email)
    users_client.create_user(payload)
    created_user_cleanup.append(unique_email)

    response = users_client.get_user(unique_email)
    assert response.status_code == 200
    assert response.json()["email"] == unique_email
    User.model_validate(response.json())


def test_get_user_returns_404_for_unknown_email(users_client):
    response = users_client.get_user("qa-does-not-exist@sdet-test.dev")
    assert response.status_code == 404
    assert "error" in response.json()


@pytest.mark.characterization
def test_get_user_handles_malformed_email_path_gracefully(users_client):
    response = users_client.get_user("not-an-email")
    assert response.status_code in (400, 404)
