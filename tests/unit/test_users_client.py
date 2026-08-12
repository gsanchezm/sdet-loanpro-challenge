import requests_mock
from src.clients.base_client import BaseClient
from src.clients.users_client import UsersClient

BASE_URL = "https://example.onrender.com/dev"

def make_client():
    return UsersClient(BaseClient(BASE_URL), auth_token="mysecrettoken")

def test_create_user_posts_payload_to_users_endpoint():
    client = make_client()
    with requests_mock.Mocker() as m:
        m.post(f"{BASE_URL}/users", json={"name": "Jane", "email": "jane@example.com", "age": 30}, status_code=201)
        response = client.create_user({"name": "Jane", "email": "jane@example.com", "age": 30})
    assert response.status_code == 201
    assert m.last_request.json() == {"name": "Jane", "email": "jane@example.com", "age": 30}

def test_delete_user_sends_authentication_header_by_default():
    client = make_client()
    with requests_mock.Mocker() as m:
        m.delete(f"{BASE_URL}/users/jane@example.com", status_code=204)
        client.delete_user("jane@example.com")
    assert m.last_request.headers["Authentication"] == "mysecrettoken"

def test_delete_user_allows_sending_no_auth_header():
    client = make_client()
    with requests_mock.Mocker() as m:
        m.delete(f"{BASE_URL}/users/jane@example.com", status_code=401)
        response = client.delete_user("jane@example.com", headers={})
    assert response.status_code == 401
    assert "Authentication" not in m.last_request.headers
