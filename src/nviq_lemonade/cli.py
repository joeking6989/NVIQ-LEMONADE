from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

from .cases import load_cases
from .client import LemonadeClient
from .comparison import compare_models
from .errors import LemonadeError
from .reporting import write_comparison, write_report
from .runner import run_suite


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nviq-lemonade",
        description="Cognitive + performance evaluation for local AI through Lemonade Server.",
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("LEMONADE_BASE_URL", "http://127.0.0.1:13305"),
        help="Lemonade Server base URL (default: %(default)s)",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("LEMONADE_API_KEY"),
        help="Optional Lemonade API key; defaults to LEMONADE_API_KEY.",
    )
    parser.add_argument("--timeout", type=float, default=60.0, help="HTTP timeout in seconds (default: 60).")

    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="Check Lemonade health and list downloaded models.")

    run = commands.add_parser("run", help="Run the public NVIQ × Lemonade v0.2 suite for one model.")
    run.add_argument("--model", required=True, help="Downloaded Lemonade model ID to evaluate.")
    run.add_argument("--cases", type=Path, help="Optional path to a public case JSON file.")
    run.add_argument("--output-dir", type=Path, default=Path("out/nviq-lemonade"), help="Report output directory.")

    compare = commands.add_parser("compare", help="Evaluate and compare one or more Lemonade models.")
    compare.add_argument("--model", action="append", required=True, dest="models", help="Model ID; repeat for each model.")
    compare.add_argument("--cases", type=Path, help="Optional path to a public case JSON file.")
    compare.add_argument("--output-dir", type=Path, default=Path("out/compare"), help="Comparison bundle output directory.")

    demo = commands.add_parser("demo", help="One-command reviewer demo using downloaded local Lemonade models.")
    demo.add_argument("--model", action="append", dest="models", help="Optional explicit model ID; repeat to compare models.")
    demo.add_argument("--max-models", type=int, default=2, help="Maximum auto-discovered local models to evaluate (default: 2).")
    demo.add_argument("--cases", type=Path, help="Optional path to a public case JSON file.")
    demo.add_argument("--output-dir", type=Path, default=Path("out/demo"), help="Reviewer bundle output directory.")
    return parser


def _client(args) -> LemonadeClient:
    return LemonadeClient(args.base_url, api_key=args.api_key, timeout_s=args.timeout)


def _select_demo_models(inventory: list[dict], *, explicit: list[str] | None, max_models: int) -> list[str]:
    if max_models < 1:
        raise ValueError("--max-models must be at least 1")
    if explicit:
        return list(explicit)

    models: list[str] = []
    for row in inventory:
        if not isinstance(row, dict):
            continue
        model_id = row.get("id")
        if not isinstance(model_id, str) or not model_id.strip():
            continue
        if row.get("downloaded") is False or row.get("recipe") == "cloud":
            continue
        models.append(model_id)
    if not models:
        raise ValueError("No downloaded local models found. Install a local model in Lemonade or pass --model explicitly.")
    return models[:max_models]


def _safe_model_dir(model_id: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", model_id).strip("-._") or "model"
    digest = hashlib.sha256(model_id.encode("utf-8")).hexdigest()[:8]
    return f"{stem[:72]}-{digest}"


def _write_bundle(comparison: dict, output_dir: Path) -> tuple[Path, Path, Path]:
    for report in comparison.get("reports", []):
        model_id = str(report.get("model", {}).get("id", "unknown"))
        write_report(report, output_dir / "models" / _safe_model_dir(model_id))
    return write_comparison(comparison, output_dir)


def _doctor(args) -> int:
    client = _client(args)
    health = client.health()
    models = client.models()
    system_info = client.system_info()
    print(f"Lemonade: {health.get('status', 'unknown')} (version {health.get('version', 'unknown')})")
    print(f"Base URL: {client.base_url}")
    print(f"Downloaded/available models: {len(models)}")
    for model in models:
        marker = "cloud" if model.get("recipe") == "cloud" else "local"
        print(f"  - {model.get('id', '<unknown>')} [{model.get('recipe', 'unknown')}; {marker}]")
    if system_info:
        print("System info:")
        print(json.dumps(system_info, indent=2, sort_keys=True))
    if not models:
        print("No models found. Install a model in Lemonade before running the suite.")
    return 0


def _run(args) -> int:
    client = _client(args)
    cases = load_cases(args.cases)
    report = run_suite(client, args.model, cases)
    json_path, md_path, html_path = write_report(report, args.output_dir)
    summary = report["summary"]
    print(f"Model: {args.model}")
    print(f"Open-suite pass rate: {summary['pass_rate'] * 100:.1f}% ({summary['passed']}/{summary['cases']})")
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {md_path}")
    print(f"HTML report: {html_path}")
    return 0


def _compare(args) -> int:
    client = _client(args)
    cases = load_cases(args.cases)
    comparison = compare_models(client, args.models, cases)
    json_path, md_path, html_path = _write_bundle(comparison, args.output_dir)
    print("Ranking: " + " > ".join(comparison["ranking"]))
    print(f"JSON comparison: {json_path}")
    print(f"Markdown comparison: {md_path}")
    print(f"HTML comparison: {html_path}")
    return 0


def _demo(args) -> int:
    client = _client(args)
    inventory = client.models()
    models = _select_demo_models(inventory, explicit=args.models, max_models=args.max_models)
    print("Reviewer demo models: " + ", ".join(models))
    cases = load_cases(args.cases)
    comparison = compare_models(client, models, cases)
    json_path, md_path, html_path = _write_bundle(comparison, args.output_dir)
    print(f"Behavioral leader: {comparison['best_behavioral_model']}")
    print(f"Open this report: {html_path}")
    print(f"Machine-readable results: {json_path}")
    print(f"Markdown results: {md_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            return _doctor(args)
        if args.command == "run":
            return _run(args)
        if args.command == "compare":
            return _compare(args)
        if args.command == "demo":
            return _demo(args)
    except (LemonadeError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
