from __future__ import annotations

import time

from .errors import LemonadeError
from .evaluation import evaluate_case


SUITE_NAME = "NVIQ × Lemonade Open Evaluation v0.1"


def _assistant_text(completion: dict) -> str:
    try:
        content = completion["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LemonadeError("Lemonade completion did not contain choices[0].message.content") from exc
    if not isinstance(content, str) or not content.strip():
        raise LemonadeError("Lemonade completion contained empty assistant content")
    return content


def run_suite(client, model: str, cases: list[dict]) -> dict:
    health = client.health()
    system_info = client.system_info()
    model_rows = client.models()
    model_info = next((row for row in model_rows if row.get("id") == model), {"id": model})

    results: list[dict] = []
    total_wall_time_ms = 0.0
    for case in cases:
        started = time.perf_counter()
        completion = client.chat(model, case["messages"], temperature=0.0)
        wall_time_ms = round((time.perf_counter() - started) * 1000.0, 3)
        total_wall_time_ms += wall_time_ms
        response_text = _assistant_text(completion)
        evaluation = evaluate_case(case, response_text)
        results.append(
            {
                "case_id": case["case_id"],
                "family": case["family"],
                "response": response_text,
                "wall_time_ms": wall_time_ms,
                "lemonade_stats": client.stats(),
                "evaluation": evaluation,
            }
        )

    passed = sum(1 for row in results if row["evaluation"]["pass"])
    count = len(results)
    return {
        "schema_version": "0.1",
        "suite": SUITE_NAME,
        "lemonade": {
            "health": health,
            "system_info": system_info,
        },
        "model": model_info,
        "summary": {
            "cases": count,
            "passed": passed,
            "failed": count - passed,
            "pass_rate": round(passed / count, 4) if count else 0.0,
            "total_wall_time_ms": round(total_wall_time_ms, 3),
        },
        "results": results,
    }
