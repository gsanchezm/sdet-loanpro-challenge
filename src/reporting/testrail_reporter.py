# src/reporting/testrail_reporter.py
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from src.config.testrail_settings import get_testrail_settings
from src.reporting.testrail_client import TestRailClient
from src.reporting.junit_parser import parse_results, group_by_function

_CASE_IDS_FILE = Path(__file__).resolve().parents[2] / "tests" / "data" / "testrail_case_ids.json"

STATUS_ID = {True: 1, False: 5}


def _format_comment(group: dict) -> str:
    lines = [f"[{variant['variant_id'] or 'no-variant'}] {'PASSED' if variant['passed'] else 'FAILED: ' + (variant['message'] or '')}" for variant in group["variants"]]
    return "\n".join(lines)


def build_results(grouped: dict[str, dict], function_to_case_id: dict[str, int]) -> list[dict]:
    unmapped = [function for function in grouped if function not in function_to_case_id]
    for function in unmapped:
        print(f"WARNING: no TestRail case mapped for {function!r} — run case_sync.py if this is a new test")

    known_functions = [function for function in grouped if function in function_to_case_id]
    return [
        {
            "case_id": function_to_case_id[function],
            "status_id": STATUS_ID[grouped[function]["passed"]],
            "comment": _format_comment(grouped[function]),
        }
        for function in known_functions
    ]


def write_step_summary(environment_label: str, results: list[dict], run_url: str) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    passed = sum(1 for result in results if result["status_id"] == 1)
    failed = len(results) - passed
    lines = [
        f"### TestRail — {environment_label}",
        "",
        f"| Cases reported | Passed | Failed |",
        f"|---|---|---|",
        f"| {len(results)} | {passed} | {failed} |",
        "",
        f"[View run in TestRail]({run_url})",
        "",
    ]
    with open(summary_path, "a") as handle:
        handle.write("\n".join(lines) + "\n")


def main(junit_xml_path: str, environment_label: str) -> None:
    function_to_case_id = json.loads(_CASE_IDS_FILE.read_text())
    grouped = group_by_function(parse_results(junit_xml_path))
    results = build_results(grouped, function_to_case_id)

    settings = get_testrail_settings()
    client = TestRailClient(settings.base_url, settings.username, settings.api_key)
    suite_id = client.get_suites(settings.project_id)[0]["id"]

    run_label = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    run = client.add_run(settings.project_id, suite_id, f"{environment_label} - {run_label}", [r["case_id"] for r in results])
    client.add_results_for_cases(run["id"], results)

    run_url = f"{settings.base_url.rstrip('/')}/index.php?/runs/view/{run['id']}"
    print(f"Reported {len(results)} case results to {run_url}")
    write_step_summary(environment_label, results, run_url)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
