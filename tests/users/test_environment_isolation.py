# tests/users/test_environment_isolation.py
from tests.conftest import client_for
from src.factories.user_factory import UserFactory


def test_user_created_in_dev_is_not_visible_in_prod():
    dev_client = client_for("dev")
    prod_client = client_for("prod")
    email = None
    try:
        payload = UserFactory.valid_payload()
        email = payload["email"]
        create_response = dev_client.create_user(payload)
        assert create_response.status_code == 201

        assert dev_client.get_user(email).status_code == 200
        assert prod_client.get_user(email).status_code == 404
    finally:
        if email:
            dev_client.delete_user(email)
            prod_client.delete_user(email)


def test_user_created_in_prod_is_not_visible_in_dev():
    dev_client = client_for("dev")
    prod_client = client_for("prod")
    email = None
    try:
        payload = UserFactory.valid_payload()
        email = payload["email"]
        create_response = prod_client.create_user(payload)
        assert create_response.status_code == 201

        assert prod_client.get_user(email).status_code == 200
        assert dev_client.get_user(email).status_code == 404
    finally:
        if email:
            dev_client.delete_user(email)
            prod_client.delete_user(email)


def test_identical_payload_behaves_the_same_in_both_environments():
    """The spec states 'identical behavior' between /dev and /prod. Any divergence
    in status code for the same invalid input is itself a bug, independent of
    which status code is 'correct'."""
    invalid_payload = {"name": "Jane Doe"}  # missing email and age
    dev_response = client_for("dev").create_user(invalid_payload)
    prod_response = client_for("prod").create_user(invalid_payload)
    assert dev_response.status_code == prod_response.status_code
