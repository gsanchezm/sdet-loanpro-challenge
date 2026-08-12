# tests/users/test_validation_boundaries.py
import pytest
from src.factories.user_factory import UserPayloadBuilder


@pytest.mark.parametrize("age", [1, 150])
def test_create_user_accepts_boundary_ages(users_client, unique_email, created_user_cleanup, age):
    payload = UserPayloadBuilder().with_email(unique_email).with_age(age).build()
    response = users_client.create_user(payload)
    created_user_cleanup.append(unique_email)
    assert response.status_code == 201
    assert response.json()["age"] == age


@pytest.mark.parametrize("age", [0, -1, 151, 1000])
def test_create_user_rejects_out_of_range_ages(users_client, unique_email, age):
    payload = UserPayloadBuilder().with_email(unique_email).with_age(age).build()
    response = users_client.create_user(payload)
    assert response.status_code == 400


@pytest.mark.parametrize("age", [25.5, "30", None])
def test_create_user_rejects_non_integer_ages(users_client, unique_email, age):
    payload = UserPayloadBuilder().with_email(unique_email).with_age(age).build()
    response = users_client.create_user(payload)
    assert response.status_code == 400


@pytest.mark.parametrize("email", ["not-an-email", "missing-at-sign.com", "", "   "])
def test_create_user_rejects_invalid_email_format(users_client, email, created_user_cleanup):
    payload = UserPayloadBuilder().with_email(email).build()
    response = users_client.create_user(payload)
    # The API is expected to reject these as 400, but if it doesn't (candidate bug),
    # the user is genuinely persisted and must not be left orphaned on dev/prod.
    if response.status_code == 201:
        created_user_cleanup.append(email)
    assert response.status_code == 400


def test_error_response_has_consistent_shape_across_endpoints(users_client):
    responses = [
        users_client.get_user("qa-does-not-exist@sdet-test.dev"),
        users_client.create_user(UserPayloadBuilder().without_field("email").build()),
        users_client.delete_user("qa-does-not-exist@sdet-test.dev"),
    ]
    for response in responses:
        assert response.status_code >= 400
        body = response.json()
        assert isinstance(body, dict)
        assert "error" in body
        assert isinstance(body["error"], str)
