#!/usr/bin/env python3
from __future__ import annotations

import compileall
import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    print("[verify] pytest", flush=True)
    tests = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=root, check=False)
    if tests.returncode:
        return tests.returncode

    print("[verify] compileall src", flush=True)
    if not compileall.compile_dir(root / "src", quiet=1):
        return 1

    print("[verify] OK", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
