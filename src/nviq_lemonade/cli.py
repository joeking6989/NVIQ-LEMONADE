from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .cases import load_cases
from .client import LemonadeClient
from .errors import LemonadeError
from .reporting import write_report
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

    run = commands.add_parser("run", help="Run the public NVIQ × Lemonade v0.1 suite.")
    run.add_argument("--model", required=True, help="Downloaded Lemonade model ID to evaluate.")
    run.add_argument("--cases", type=Path, help="Optional path to a public case JSON file.")
    run.add_argument("--output-dir", type=Path, default=Path("out/nviq-lemonade"), help="Report output directory.")
    return parser


def _client(args) -> LemonadeClient:
    return LemonadeClient(args.base_url, api_key=args.api_key, timeout_s=args.timeout)


def _doctor(args) -> int:
    client = _client(args)
    health = client.health()
    models = client.models()
    system_info = client.system_info()
    print(f"Lemonade: {health.get('status', 'unknown')} (version {health.get('version', 'unknown')})")
    print(f"Base URL: {client.base_url}")
    print(f"Downloaded models: {len(models)}")
    for model in models:
        print(f"  - {model.get('id', '<unknown>')} [{model.get('recipe', 'unknown')}]")
    if system_info:
        print("System info:")
        print(json.dumps(system_info, indent=2, sort_keys=True))
    if not models:
        print("No downloaded models found. Install a model in Lemonade before running the suite.")
    return 0


def _run(args) -> int:
    client = _client(args)
    cases = load_cases(args.cases)
    report = run_suite(client, args.model, cases)
    json_path, md_path = write_report(report, args.output_dir)
    summary = report["summary"]
    print(f"Model: {args.model}")
    print(f"Open-suite pass rate: {summary['pass_rate'] * 100:.1f}% ({summary['passed']}/{summary['cases']})")
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {md_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            return _doctor(args)
        if args.command == "run":
            return _run(args)
    except (LemonadeError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
