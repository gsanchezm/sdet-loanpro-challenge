import xml.etree.ElementTree as ET

def _split_function_and_variant(test_name: str) -> tuple[str, str | None]:
    if "[" not in test_name:
        return test_name, None
    function, _, remainder = test_name.partition("[")
    return function, remainder.rstrip("]")


def parse_results(junit_xml_path: str) -> list[dict]:
    root = ET.parse(junit_xml_path).getroot()
    results = []
    for testcase in root.iter("testcase"):
        function, variant_id = _split_function_and_variant(testcase.get("name"))
        failure = testcase.find("failure")
        error = testcase.find("error")
        outcome_node = failure if failure is not None else error
        results.append({
            "function": function,
            "variant_id": variant_id,
            "passed": outcome_node is None,
            "message": outcome_node.get("message") if outcome_node is not None else None,
        })
    return results


def group_by_function(results: list[dict]) -> dict[str, dict]:
    grouped: dict[str, dict] = {}
    for result in results:
        group = grouped.setdefault(result["function"], {"passed": True, "variants": []})
        group["variants"].append(result)
        group["passed"] = group["passed"] and result["passed"]
    return grouped
