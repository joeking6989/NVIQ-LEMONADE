from __future__ import annotations

import json
from pathlib import Path

from .html_reporting import comparison_html, single_report_html


def _markdown(report: dict) -> str:
    model_id = report.get("model", {}).get("id", "unknown")
    summary = report.get("summary", {})
    performance = report.get("performance", {})
    pass_rate = float(summary.get("pass_rate", 0.0)) * 100.0
    health = report.get("lemonade", {}).get("health") or {}
    system_info = report.get("lemonade", {}).get("system_info")

    lines = [
        "# NVIQ × Lemonade Evaluation Report",
        "",
        f"**Suite:** {report.get('suite', 'unknown')}",
        f"**Model:** `{model_id}`",
        f"**Lemonade status:** {health.get('status', 'unknown')}",
        f"**Lemonade version:** {health.get('version', 'unknown')}",
        f"**Pass rate:** {pass_rate:.1f}% ({summary.get('passed', 0)}/{summary.get('cases', 0)})",
        f"**Total wall time:** {summary.get('total_wall_time_ms', 0)} ms",
        f"**Mean tokens/sec:** {performance.get('mean_tokens_per_second') if performance.get('mean_tokens_per_second') is not None else 'unavailable'}",
        f"**Mean TTFT:** {performance.get('mean_time_to_first_token_s') if performance.get('mean_time_to_first_token_s') is not None else 'unavailable'}",
        "",
    ]
    if system_info:
        lines.extend(["## Local system", "", "```json", json.dumps(system_info, indent=2, sort_keys=True), "```", ""])

    lines.extend([
        "## Case results",
        "",
        "| Case | Family | Result | Wall time | Evaluation evidence |",
        "|---|---|---:|---:|---|",
    ])
    for row in report.get("results", []):
        evaluation = row.get("evaluation", {})
        status = "PASS" if evaluation.get("pass") else "FAIL"
        evidence = str(evaluation.get("evidence", "")).replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| `{row.get('case_id', '')}` | {row.get('family', '')} | **{status}** | "
            f"{row.get('wall_time_ms', 0)} ms | {evidence} |"
        )

    lines.extend([
        "",
        "> Host-resource values are post-inference /v1/system-stats samples; maxima are maxima across those samples, not continuous in-request peaks.",
        "",
        "> This report is produced by the open NVIQ × Lemonade evaluation suite. It is not a full NVIQ certification or Noct-Tech Reliability Audit.",
        "",
    ])
    return "\n".join(lines)


def _comparison_markdown(comparison: dict) -> str:
    rows_by_id = {str(row.get("model_id")): row for row in comparison.get("models", [])}
    lines = [
        "# NVIQ × Lemonade Model Comparison",
        "",
        "**Ranking policy:** behavioral pass rate first, then mean tokens/sec when available, then lower mean wall-clock latency.",
        f"**Behavioral leader:** `{comparison.get('best_behavioral_model', 'unknown')}`",
        "",
        "| Rank | Model | Behavior | Mean tok/s | Mean TTFT | Mean wall | Max sampled GPU | Max sampled NPU |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for index, model_id in enumerate(comparison.get("ranking", []), start=1):
        row = rows_by_id.get(str(model_id), {})
        pass_rate = float(row.get("pass_rate", 0.0)) * 100.0

        def value(key):
            item = row.get(key)
            return item if item is not None else "—"

        lines.append(
            f"| {index} | `{model_id}` | {pass_rate:.1f}% ({row.get('passed', 0)}/{row.get('cases', 0)}) | "
            f"{value('mean_tokens_per_second')} | {value('mean_time_to_first_token_s')} | {value('mean_wall_time_ms')} | "
            f"{value('peak_gpu_percent')} | {value('peak_npu_percent')} |"
        )
    lines.extend([
        "",
        "> GPU/NPU values are maxima across post-inference `/v1/system-stats` samples, not continuous in-request peaks.",
        "",
        "> This ordering is a transparent public-demo heuristic, not the proprietary canonical NVIQ scorer.",
        "",
    ])
    return "\n".join(lines)


def write_report(report: dict, output_dir: Path | str) -> tuple[Path, Path, Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "report.json"
    md_path = directory / "report.md"
    html_path = directory / "report.html"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(report), encoding="utf-8")
    html_path.write_text(single_report_html(report), encoding="utf-8")
    return json_path, md_path, html_path


def write_comparison(comparison: dict, output_dir: Path | str) -> tuple[Path, Path, Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "comparison.json"
    md_path = directory / "comparison.md"
    html_path = directory / "comparison.html"
    json_path.write_text(json.dumps(comparison, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(_comparison_markdown(comparison), encoding="utf-8")
    html_path.write_text(comparison_html(comparison), encoding="utf-8")
    return json_path, md_path, html_path
