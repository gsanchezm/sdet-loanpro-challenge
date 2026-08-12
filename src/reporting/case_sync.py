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

def _case_fields(entry: dict) -> dict:
    return {
        "custom_preconds": entry["preconditions"],
        "custom_steps": entry["steps"],
        "custom_expected": entry["expected_result"],
    }

def _sync_one_case(client: TestRailClient, section_id: int, existing: dict[str, int], entry: dict) -> int:
    fields = _case_fields(entry)
    case_id = existing.get(entry["title"])
    if case_id is not None:
        client.update_case(case_id, **fields)
        return case_id
    return client.add_case(section_id, entry["title"], **fields)["id"]

def _ensure_cases(client: TestRailClient, project_id: int, suite_id: int, section_id: int, entries: list[dict]) -> dict[str, int]:
    existing = {case["title"]: case["id"] for case in client.get_cases(project_id, suite_id, section_id)}
    return {entry["title"]: _sync_one_case(client, section_id, existing, entry) for entry in entries}

def sync_cases(client: TestRailClient, project_id: int, catalog: list[dict]) -> dict[str, int]:
    suite_id = client.get_default_suite_id(project_id)
    section_names = sorted({entry["section"] for entry in catalog})
    section_ids = _ensure_sections(client, project_id, suite_id, section_names)

    function_to_case_id: dict[str, int] = {}
    for section_name in section_names:
        section_entries = [entry for entry in catalog if entry["section"] == section_name]
        title_to_case_id = _ensure_cases(client, project_id, suite_id, section_ids[section_name], section_entries)
        for entry in section_entries:
            function_to_case_id[entry["function"]] = title_to_case_id[entry["title"]]
    return function_to_case_id


def main() -> None:
    settings = get_testrail_settings()
    client = TestRailClient(settings.base_url, settings.username, settings.api_key)
    catalog = json.loads(_CATALOG_FILE.read_text(encoding="utf-8"))
    function_to_case_id = sync_cases(client, settings.project_id, catalog)
    _CASE_IDS_FILE.write_text(json.dumps(function_to_case_id, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Synced {len(function_to_case_id)} cases -> {_CASE_IDS_FILE}")


if __name__ == "__main__":
    sys.exit(main())
