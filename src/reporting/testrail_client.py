import requests


class TestRailClient:
    def __init__(self, base_url: str, username: str, api_key: str):
        self._api_url = base_url.rstrip("/") + "/index.php"
        self._auth = (username, api_key)

    def _get(self, endpoint: str):
        response = requests.get(f"{self._api_url}?/api/v2/{endpoint}", auth=self._auth)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint: str, payload: dict):
        response = requests.post(f"{self._api_url}?/api/v2/{endpoint}", auth=self._auth, json=payload)
        response.raise_for_status()
        return response.json()

    def get_suites(self, project_id: int) -> list[dict]:
        return self._get(f"get_suites/{project_id}")["suites"]

    def get_sections(self, project_id: int, suite_id: int) -> list[dict]:
        return self._get(f"get_sections/{project_id}&suite_id={suite_id}")["sections"]

    def add_section(self, project_id: int, suite_id: int, name: str) -> dict:
        return self._post(f"add_section/{project_id}", {"name": name, "suite_id": suite_id})

    def get_cases(self, project_id: int, suite_id: int, section_id: int) -> list[dict]:
        return self._get(f"get_cases/{project_id}&suite_id={suite_id}&section_id={section_id}")["cases"]

    def add_case(self, section_id: int, title: str) -> dict:
        return self._post(f"add_case/{section_id}", {"title": title})

    def add_run(self, project_id: int, suite_id: int, name: str, case_ids: list[int]) -> dict:
        return self._post(f"add_run/{project_id}", {
            "suite_id": suite_id,
            "name": name,
            "include_all": False,
            "case_ids": case_ids,
        })

    def add_results_for_cases(self, run_id: int, results: list[dict]) -> list[dict]:
        return self._post(f"add_results_for_cases/{run_id}", {"results": results})

    def get_runs(self, project_id: int) -> list[dict]:
        return self._get(f"get_runs/{project_id}")["runs"]
