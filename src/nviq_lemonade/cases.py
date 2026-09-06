from __future__ import annotations

import json
from pathlib import Path


_DEFAULT_CASES = Path(__file__).resolve().parents[2] / "cases" / "v0.1" / "public.json"


def load_cases(path: Path | str | None = None) -> list[dict]:
    source = Path(path) if path is not None else _DEFAULT_CASES
    data = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("public case file must contain a JSON array")
    required = {"case_id", "family", "messages", "rule", "expected"}
    seen: set[str] = set()
    for case in data:
        if not isinstance(case, dict) or not required.issubset(case):
            raise ValueError("each public case must contain case_id, family, messages, rule, and expected")
        case_id = str(case["case_id"])
        if case_id in seen:
            raise ValueError(f"duplicate case_id: {case_id}")
        seen.add(case_id)
    return data
