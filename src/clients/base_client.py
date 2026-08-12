import requests


class BaseClient:
    def __init__(self, base_url: str):
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()

    def _url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    def get(self, path: str, **kwargs) -> requests.Response:
        return self._session.get(self._url(path), **kwargs)

    def post(self, path: str, json: dict, **kwargs) -> requests.Response:
        return self._session.post(self._url(path), json=json, **kwargs)

    def put(self, path: str, json: dict, **kwargs) -> requests.Response:
        return self._session.put(self._url(path), json=json, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self._session.delete(self._url(path), **kwargs)
