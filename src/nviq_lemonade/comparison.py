from __future__ import annotations

import math

from .runner import run_suite


def _number(value, default: float) -> float:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return default


def _comparison_row(report: dict) -> dict:
    summary = report.get("summary", {})
    performance = report.get("performance", {})
    model = report.get("model", {})
    return {
        "model_id": str(model.get("id", "unknown")),
        "recipe": model.get("recipe"),
        "pass_rate": _number(summary.get("pass_rate"), 0.0),
        "passed": int(summary.get("passed", 0)),
        "cases": int(summary.get("cases", 0)),
        "mean_tokens_per_second": performance.get("mean_tokens_per_second"),
        "mean_time_to_first_token_s": performance.get("mean_time_to_first_token_s"),
        "mean_wall_time_ms": performance.get("mean_wall_time_ms"),
        "peak_cpu_percent": performance.get("peak_cpu_percent"),
        "peak_gpu_percent": performance.get("peak_gpu_percent"),
        "peak_vram_gb": performance.get("peak_vram_gb"),
        "peak_npu_percent": performance.get("peak_npu_percent"),
    }


def _ranking_key(row: dict) -> tuple:
    pass_rate = _number(row.get("pass_rate"), 0.0)
    tokens_per_second = _number(row.get("mean_tokens_per_second"), -math.inf)
    wall_time_ms = _number(row.get("mean_wall_time_ms"), math.inf)
    return (-pass_rate, -tokens_per_second, wall_time_ms, row.get("model_id", ""))


def compare_models(client, models: list[str], cases: list[dict]) -> dict:
    if not models:
        raise ValueError("comparison requires at least one model")
    if len(set(models)) != len(models):
        raise ValueError("comparison model list contains duplicate model IDs")

    reports = [run_suite(client, model, cases) for model in models]
    rows = [_comparison_row(report) for report in reports]
    ranked = sorted(rows, key=_ranking_key)
    ranking = [row["model_id"] for row in ranked]
    best_behavioral_model = ranking[0] if ranking else None

    return {
        "schema_version": "0.2",
        "suite": "NVIQ × Lemonade Model Comparison v0.2",
        "ranking_policy": [
            "higher public-suite pass rate",
            "higher mean tokens per second when available",
            "lower mean wall-clock latency",
        ],
        "models": rows,
        "ranking": ranking,
        "best_behavioral_model": best_behavioral_model,
        "reports": reports,
    }
