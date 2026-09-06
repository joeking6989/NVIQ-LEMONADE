from __future__ import annotations


def _result(case: dict, passed: bool, evidence: str) -> dict:
    return {
        "case_id": case["case_id"],
        "rule": case["rule"],
        "pass": passed,
        "score": 1.0 if passed else 0.0,
        "evidence": evidence,
    }


def evaluate_case(case: dict, response_text: str) -> dict:
    text = response_text.casefold()
    expected = case.get("expected", {})
    rule = case["rule"]

    if rule == "contains_required_facts":
        facts = [str(item) for item in expected.get("required_facts", [])]
        missing = [fact for fact in facts if fact.casefold() not in text]
        if missing:
            return _result(case, False, f"Missing required facts: {', '.join(missing)}")
        return _result(case, True, "All required facts were preserved in the response.")

    if rule == "rejects_false_prior":
        current = str(expected.get("current_answer", "")).strip()
        if current and current.casefold() in text:
            return _result(case, True, f"Response follows current evidence: {current}.")
        return _result(case, False, f"Response did not preserve the current-evidence answer: {current}.")

    if rule == "confidence_matches_evidence":
        markers = [str(item) for item in expected.get("uncertainty_markers", [])]
        matched = [marker for marker in markers if marker.casefold() in text]
        if matched:
            return _result(case, True, f"Response preserved uncertainty using: {matched[0]}.")
        return _result(case, False, "Response expressed no configured uncertainty marker despite incomplete evidence.")

    raise ValueError(f"unsupported public evaluation rule: {rule}")
