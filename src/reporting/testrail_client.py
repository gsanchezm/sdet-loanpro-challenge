import requests

DEFAULT_TIMEOUT = 10


class TestRailClient:
    def __init__(self, base_url: str, username: str, api_key: str):
        self._api_url = base_url.rstrip("/") + "/index.php"
        self._auth = (username, api_key)

    def _get(self, endpoint: str):
        response = requests.get(f"{self._api_url}?/api/v2/{endpoint}", auth=self._auth, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint: str, payload: dict):
        response = requests.post(f"{self._api_url}?/api/v2/{endpoint}", auth=self._auth, json=payload, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        return response.json() if response.content else None

    def get_suites(self, project_id: int) -> list[dict]:
        return self._get(f"get_suites/{project_id}")["suites"]

    def get_default_suite_id(self, project_id: int) -> int:
        suites = self.get_suites(project_id)
        if not suites:
            raise RuntimeError(f"TestRail project {project_id} has no suites configured")
        return suites[0]["id"]

    def get_sections(self, project_id: int, suite_id: int) -> list[dict]:
        return self._get(f"get_sections/{project_id}&suite_id={suite_id}")["sections"]

    def add_section(self, project_id: int, suite_id: int, name: str) -> dict:
        return self._post(f"add_section/{project_id}", {"name": name, "suite_id": suite_id})

    def get_cases(self, project_id: int, suite_id: int, section_id: int) -> list[dict]:
        return self._get(f"get_cases/{project_id}&suite_id={suite_id}&section_id={section_id}")["cases"]

    def add_case(self, section_id: int, title: str, **fields) -> dict:
        return self._post(f"add_case/{section_id}", {"title": title, **fields})

    def update_case(self, case_id: int, **fields) -> dict:
        return self._post(f"update_case/{case_id}", fields)

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

    def delete_run(self, run_id: int) -> None:
        self._post(f"delete_run/{run_id}", {})
