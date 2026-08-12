import json
import sys
from pathlib import Path

from src.config.testrail_settings import get_testrail_settings
from src.reporting.testrail_client import TestRailClient

_CATALOG_FILE = Path(__file__).resolve().parents[2] / "tests" / "data" / "testrail_cases.json"
_CASE_IDS_FILE = Path(__file__).resolve().parents[2] / "tests" / "data" / "testrail_case_ids.json"


def _ensure_sections(client: TestRailClient, project_id: int, suite_id: int, section_names: list[str]) -> dict[str, int]:
    existing = {section["name"]: section["id"] for section in client.get_sections(project_id, suite_id)}
    missing = [name for name in section_names if name not in existing]
    created = {name: client.add_section(project_id, suite_id, name)["id"] for name in missing}
    return {**existing, **created}

def _ensure_cases(client: TestRailClient, project_id: int, suite_id: int, section_id: int, titles: list[str]) -> dict[str, int]:
    existing = {case["title"]: case["id"] for case in client.get_cases(project_id, suite_id, section_id)}
    missing = [title for title in titles if title not in existing]
    created = {title: client.add_case(section_id, title)["id"] for title in missing}
    return {**existing, **created}

def sync_cases(client: TestRailClient, project_id: int, catalog: list[dict]) -> dict[str, int]:
    suite_id = client.get_suites(project_id)[0]["id"]
    section_names = sorted({entry["section"] for entry in catalog})
    section_ids = _ensure_sections(client, project_id, suite_id, section_names)

    function_to_case_id: dict[str, int] = {}
    for section_name in section_names:
        section_entries = [entry for entry in catalog if entry["section"] == section_name]
        titles = [entry["title"] for entry in section_entries]
        title_to_case_id = _ensure_cases(client, project_id, suite_id, section_ids[section_name], titles)
        for entry in section_entries:
            function_to_case_id[entry["function"]] = title_to_case_id[entry["title"]]
    return function_to_case_id


def main() -> None:
    settings = get_testrail_settings()
    client = TestRailClient(settings.base_url, settings.username, settings.api_key)
    catalog = json.loads(_CATALOG_FILE.read_text())
    function_to_case_id = sync_cases(client, settings.project_id, catalog)
    _CASE_IDS_FILE.write_text(json.dumps(function_to_case_id, indent=2, sort_keys=True) + "\n")
    print(f"Synced {len(function_to_case_id)} cases -> {_CASE_IDS_FILE}")


if __name__ == "__main__":
    sys.exit(main())
