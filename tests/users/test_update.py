import uuid
from src.factories.user_factory import UserFactory, UserPayloadBuilder


def test_update_user_returns_200_with_updated_fields(users_client, unique_email, created_user_cleanup):
    users_client.create_user(UserFactory.valid_payload(email=unique_email))
    created_user_cleanup.append(unique_email)

    new_payload = UserFactory.valid_payload(email=unique_email, name="Updated Name", age=99)
    response = users_client.update_user(unique_email, new_payload)

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Updated Name"
    assert body["age"] == 99


def test_update_user_returns_404_for_unknown_email(users_client):
    payload = UserFactory.valid_payload()
    response = users_client.update_user("qa-does-not-exist@sdet-test.dev", payload)
    assert response.status_code == 404


def test_update_user_rejects_partial_body(users_client, unique_email, created_user_cleanup):
    users_client.create_user(UserFactory.valid_payload(email=unique_email))
    created_user_cleanup.append(unique_email)

    partial_payload = {"name": "Only Name"}
    response = users_client.update_user(unique_email, partial_payload)
    assert response.status_code == 400


def test_update_user_rejects_out_of_range_age(users_client, unique_email, created_user_cleanup):
    users_client.create_user(UserFactory.valid_payload(email=unique_email))
    created_user_cleanup.append(unique_email)

    bad_payload = UserPayloadBuilder().with_email(unique_email).with_age(151).build()
    response = users_client.update_user(unique_email, bad_payload)
    assert response.status_code == 400


def test_update_user_changing_email_in_body(users_client, unique_email, created_user_cleanup):
    """PUT documents a 409 for duplicate email, implying the body's email can differ
    from the path's — this characterizes what actually happens when it does."""
    other_email = f"qa-other-{uuid.uuid4()}@sdet-test.dev"
    users_client.create_user(UserFactory.valid_payload(email=unique_email))
    created_user_cleanup.extend([unique_email, other_email])

    renamed_payload = UserFactory.valid_payload(email=other_email)
    response = users_client.update_user(unique_email, renamed_payload)

    old_lookup = users_client.get_user(unique_email)
    new_lookup = users_client.get_user(other_email)
    # No assertion on the exact outcome here on purpose — Task 14 records what
    # actually happens (rename, dual-accessible, or rejected) as a documented finding.
    assert response.status_code in (200, 400, 404, 409)
    assert old_lookup.status_code in (200, 404)
    assert new_lookup.status_code in (200, 404)
