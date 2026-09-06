from __future__ import annotations

import time
from statistics import mean

from .errors import LemonadeError
from .evaluation import evaluate_case


SUITE_NAME = "NVIQ × Lemonade Open Evaluation v0.2"


def _assistant_text(completion: dict) -> str:
    try:
        content = completion["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LemonadeError("Lemonade completion did not contain choices[0].message.content") from exc
    if not isinstance(content, str) or not content.strip():
        raise LemonadeError("Lemonade completion contained empty assistant content")
    return content


def _numeric_values(rows: list[dict | None], key: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        value = row.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            values.append(float(value))
    return values


def _mean_or_none(values: list[float], *, digits: int = 4) -> float | None:
    return round(mean(values), digits) if values else None


def _sum_or_none(values: list[float]) -> int | float | None:
    if not values:
        return None
    total = sum(values)
    return int(total) if total.is_integer() else round(total, 4)


def _max_or_none(values: list[float]) -> float | None:
    return round(max(values), 4) if values else None


def _performance(results: list[dict]) -> dict:
    request_stats = [row.get("lemonade_stats") for row in results]
    system_stats = [row.get("system_stats") for row in results]
    wall_times = [float(row["wall_time_ms"]) for row in results]
    return {
        "samples": len(results),
        "mean_wall_time_ms": _mean_or_none(wall_times, digits=3),
        "mean_time_to_first_token_s": _mean_or_none(_numeric_values(request_stats, "time_to_first_token")),
        "mean_tokens_per_second": _mean_or_none(_numeric_values(request_stats, "tokens_per_second")),
        "input_tokens_total": _sum_or_none(_numeric_values(request_stats, "input_tokens")),
        "output_tokens_total": _sum_or_none(_numeric_values(request_stats, "output_tokens")),
        "peak_cpu_percent": _max_or_none(_numeric_values(system_stats, "cpu_percent")),
        "peak_memory_gb": _max_or_none(_numeric_values(system_stats, "memory_gb")),
        "peak_gpu_percent": _max_or_none(_numeric_values(system_stats, "gpu_percent")),
        "peak_vram_gb": _max_or_none(_numeric_values(system_stats, "vram_gb")),
        "peak_npu_percent": _max_or_none(_numeric_values(system_stats, "npu_percent")),
    }


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

        # /v1/stats describes the just-finished inference request, so capture it
        # before sampling the host's current system utilization.
        request_stats = client.stats()
        system_stats_method = getattr(client, "system_stats", None)
        system_stats = system_stats_method() if callable(system_stats_method) else None

        results.append(
            {
                "case_id": case["case_id"],
                "family": case["family"],
                "response": response_text,
                "wall_time_ms": wall_time_ms,
                "lemonade_stats": request_stats,
                "system_stats": system_stats,
                "evaluation": evaluation,
            }
        )

    passed = sum(1 for row in results if row["evaluation"]["pass"])
    count = len(results)
    return {
        "schema_version": "0.2",
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
        "performance": _performance(results),
        "results": results,
    }
