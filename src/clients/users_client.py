from src.clients.base_client import BaseClient


class UsersClient:
    def __init__(self, base_client: BaseClient, auth_token: str):
        self._client = base_client
        self._auth_token = auth_token

    def list_users(self):
        return self._client.get("/users")

    def create_user(self, payload: dict):
        return self._client.post("/users", json=payload)

    def get_user(self, email: str):
        return self._client.get(f"/users/{email}")

    def update_user(self, email: str, payload: dict):
        return self._client.put(f"/users/{email}", json=payload)

    def delete_user(self, email: str, *, headers: dict | None = None):
        if headers is None:
            headers = {"Authentication": self._auth_token}
        return self._client.delete(f"/users/{email}", headers=headers)
