from __future__ import annotations

import json
from pathlib import Path


def _markdown(report: dict) -> str:
    model_id = report.get("model", {}).get("id", "unknown")
    summary = report.get("summary", {})
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
        "> This report is produced by the open NVIQ × Lemonade evaluation suite. It is not a full NVIQ certification or Noct-Tech Reliability Audit.",
        "",
    ])
    return "\n".join(lines)


def write_report(report: dict, output_dir: Path | str) -> tuple[Path, Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "report.json"
    md_path = directory / "report.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(report), encoding="utf-8")
    return json_path, md_path
