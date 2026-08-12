import pytest
from src.data.loader import load_dataset
from src.factories.user_factory import UserFactory, UserPayloadBuilder


def test_create_user_returns_201_with_created_user(users_client, unique_email, created_user_cleanup):
    payload = UserFactory.valid_payload(email=unique_email)
    response = users_client.create_user(payload)
    created_user_cleanup.append(unique_email)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == unique_email
    assert body["name"] == payload["name"]
    assert body["age"] == payload["age"]


def test_create_user_rejects_duplicate_email(users_client, unique_email, created_user_cleanup):
    payload = UserFactory.valid_payload(email=unique_email)
    first = users_client.create_user(payload)
    created_user_cleanup.append(unique_email)
    assert first.status_code == 201

    second = users_client.create_user(payload)
    assert second.status_code == 409
    assert "error" in second.json()


@pytest.mark.parametrize("missing_field", load_dataset("missing_required_fields"))
def test_create_user_rejects_missing_required_field(users_client, missing_field):
    payload = UserPayloadBuilder().without_field(missing_field).build()
    response = users_client.create_user(payload)
    assert response.status_code == 400
    assert "error" in response.json()


def test_create_user_ignores_or_rejects_unknown_fields(users_client, unique_email, created_user_cleanup):
    payload = UserPayloadBuilder().with_email(unique_email).with_extra_field("role", "admin").build()
    response = users_client.create_user(payload)
    if response.status_code != 201:
        assert response.status_code == 400
        return

    created_user_cleanup.append(unique_email)
    assert "role" not in response.json()
