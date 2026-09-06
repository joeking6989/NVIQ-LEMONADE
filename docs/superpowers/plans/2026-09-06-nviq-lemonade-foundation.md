# NVIQ × Lemonade Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone, open-source NVIQ × Lemonade CLI that discovers local Lemonade models, runs a transparent public cognitive-evaluation suite, captures local runtime telemetry, and emits reproducible reports without exposing the private NVIQ scorer.

**Architecture:** A dependency-light Python 3.11+ package uses Lemonade's HTTP API directly through the standard library. Versioned public JSON cases are evaluated by transparent deterministic rules; the runner combines model responses, wall-clock timing, Lemonade telemetry, and public scores into JSON/Markdown reports.

**Tech Stack:** Python 3.11+, standard library (`urllib`, `json`, `argparse`, `dataclasses`, `pathlib`, `time`), pytest for development/testing, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-06-nviq-lemonade-foundation-design.md`

## Global Constraints

- Core runtime supports Python 3.11+.
- Core package has no third-party runtime dependencies.
- Default Lemonade base URL is `http://127.0.0.1:13305`.
- Public repository uses Apache License 2.0.
- No private NVIQ source code, proprietary scorer logic, commercial Reliability Audit implementation, private benchmark corpus, secrets, or unreleased research artifacts are copied into this repository.
- Public scores must be labeled as the NVIQ × Lemonade open evaluation suite, not as full NVIQ certification.
- Optional Lemonade telemetry endpoints may be unavailable without failing a benchmark run.

---

### Task 1: Package skeleton and public evaluation contract

**Files:**
- Create: `pyproject.toml`
- Create: `src/nviq_lemonade/__init__.py`
- Create: `src/nviq_lemonade/errors.py`
- Create: `src/nviq_lemonade/cases.py`
- Create: `src/nviq_lemonade/evaluation.py`
- Create: `cases/v0.1/public.json`
- Test: `tests/test_evaluation.py`

**Interfaces:**
- Produces: `load_cases(path: Path | None = None) -> list[dict]`
- Produces: `evaluate_case(case: dict, response_text: str) -> dict`
- Produces: `LemonadeError(RuntimeError)` for later transport use.

- [ ] **Step 1: Write failing evaluation tests**

```python
from nviq_lemonade.evaluation import evaluate_case


def test_rejects_false_prior_prefers_current_evidence():
    case = {
        "case_id": "prior-001",
        "rule": "rejects_false_prior",
        "expected": {"current_answer": "blue", "false_prior": "red"},
    }
    result = evaluate_case(case, "The current evidence says blue.")
    assert result["pass"] is True
    assert result["score"] == 1.0


def test_confidence_rule_requires_uncertainty_marker():
    case = {
        "case_id": "confidence-001",
        "rule": "confidence_matches_evidence",
        "expected": {"uncertainty_markers": ["uncertain", "not enough information"]},
    }
    result = evaluate_case(case, "It is definitely 42.")
    assert result["pass"] is False
```

- [ ] **Step 2: Run tests and verify RED**

Run: `PYTHONPATH=src python -m pytest tests/test_evaluation.py -q`
Expected: import failure because `nviq_lemonade.evaluation` does not exist.

- [ ] **Step 3: Implement minimal case loader and evaluator**

Implement only these rules:

```python
RULES = {
    "contains_required_facts",
    "rejects_false_prior",
    "confidence_matches_evidence",
}
```

`evaluate_case()` returns:

```python
{
    "case_id": case["case_id"],
    "rule": case["rule"],
    "pass": bool,
    "score": 1.0 or 0.0,
    "evidence": "human-readable explanation",
}
```

- [ ] **Step 4: Add `cases/v0.1/public.json`**

Include exactly three initial cases, one per public family: Context Integrity, Prior-Contamination Resistance, Confidence Discipline.

- [ ] **Step 5: Run tests and verify GREEN**

Run: `PYTHONPATH=src python -m pytest tests/test_evaluation.py -q`
Expected: PASS.

### Task 2: Lemonade HTTP client

**Files:**
- Create: `src/nviq_lemonade/client.py`
- Test: `tests/http_fixture.py`
- Test: `tests/test_client.py`

**Interfaces:**
- Consumes: `LemonadeError` from Task 1.
- Produces: `LemonadeClient.health() -> dict`
- Produces: `LemonadeClient.models() -> list[dict]`
- Produces: `LemonadeClient.chat(model, messages, temperature=0.0) -> dict`
- Produces: `LemonadeClient.stats() -> dict | None`
- Produces: `LemonadeClient.system_info() -> dict | None`

- [ ] **Step 1: Write failing client tests using a local HTTP server**

Test that:

```python
client.health()["status"] == "ok"
client.models()[0]["id"] == "Fixture-Model"
client.chat("Fixture-Model", [{"role": "user", "content": "hello"}])["choices"][0]["message"]["content"] == "fixture response"
client.stats()["tokens_per_second"] == 42.0
client.system_info()["os"] == "fixture-os"
```

Also assert an API key is sent as `Authorization: Bearer test-key` and that a fixture 500 response raises `LemonadeError` containing the HTTP status.

- [ ] **Step 2: Run tests and verify RED**

Run: `PYTHONPATH=src python -m pytest tests/test_client.py -q`
Expected: import failure because `client.py` does not exist.

- [ ] **Step 3: Implement standard-library HTTP transport**

Normalize `base_url` with no trailing slash. JSON requests use `Content-Type: application/json`, `Accept: application/json`, and `User-Agent: NVIQ-Lemonade/0.1`. Optional endpoints return `None` only for HTTP 404.

- [ ] **Step 4: Run tests and verify GREEN**

Run: `PYTHONPATH=src python -m pytest tests/test_client.py -q`
Expected: PASS.

### Task 3: Runner and reproducible reporting

**Files:**
- Create: `src/nviq_lemonade/runner.py`
- Create: `src/nviq_lemonade/reporting.py`
- Test: `tests/test_runner.py`
- Test: `tests/test_reporting.py`

**Interfaces:**
- Consumes: `LemonadeClient`, `load_cases`, `evaluate_case`.
- Produces: `run_suite(client: LemonadeClient, model: str, cases: list[dict]) -> dict`
- Produces: `write_report(report: dict, output_dir: Path) -> tuple[Path, Path]`

- [ ] **Step 1: Write failing runner test**

Use a fake in-process client object and assert the report contains:

```python
assert report["model"]["id"] == "Fixture-Model"
assert report["summary"]["cases"] == 3
assert report["summary"]["passed"] == 3
assert report["summary"]["pass_rate"] == 1.0
assert len(report["results"]) == 3
```

Each result must contain `wall_time_ms` and `lemonade_stats`.

- [ ] **Step 2: Run runner test and verify RED**

Run: `PYTHONPATH=src python -m pytest tests/test_runner.py -q`
Expected: import failure because `runner.py` does not exist.

- [ ] **Step 3: Implement runner minimally and make test GREEN**

Use `time.perf_counter()` around the chat call. Find selected model metadata from `client.models()`; if absent, retain `{"id": model}`.

- [ ] **Step 4: Write failing reporting test**

Call `write_report()` and assert `report.json` parses back to the same dictionary and `report.md` contains the selected model, aggregate pass rate, and every case ID.

- [ ] **Step 5: Implement deterministic JSON + Markdown writers and verify GREEN**

Run: `PYTHONPATH=src python -m pytest tests/test_runner.py tests/test_reporting.py -q`
Expected: PASS.

### Task 4: CLI and doctor workflow

**Files:**
- Create: `src/nviq_lemonade/cli.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Produces console script: `nviq-lemonade = nviq_lemonade.cli:main`
- Commands: `doctor`, `run`.

- [ ] **Step 1: Write failing parser/smoke tests**

Assert `doctor` prints server version/status plus discovered model IDs. Assert `run --model Fixture-Model --output-dir <tmp>` creates both report files when pointed at the HTTP fixture server.

- [ ] **Step 2: Verify RED**

Run: `PYTHONPATH=src python -m pytest tests/test_cli.py -q`
Expected: import failure because `cli.py` does not exist.

- [ ] **Step 3: Implement CLI**

Environment variables:

```text
LEMONADE_BASE_URL
LEMONADE_API_KEY
```

Flags:

```text
--base-url
--api-key
--timeout
```

`run` additionally accepts `--model`, `--cases`, and `--output-dir`.

- [ ] **Step 4: Verify GREEN**

Run: `PYTHONPATH=src python -m pytest tests/test_cli.py -q`
Expected: PASS.

### Task 5: Open-source challenge packaging

**Files:**
- Modify: `README.md`
- Create: `LICENSE`
- Create: `.gitignore`
- Create: `.github/workflows/ci.yml`
- Create: `docs/architecture.md`
- Create: `examples/sample-report.md`

**Interfaces:** Documentation and CI only; no production API changes.

- [ ] **Step 1: Replace bootstrap README**

README must include:

- One-sentence pitch: cognitive + performance evaluation for local AI through Lemonade.
- AMD Lemonade Developer Challenge context.
- Exact install/run commands.
- Architecture diagram.
- Public/private NVIQ boundary.
- Explanation of the three public benchmark families.
- Report schema/example.
- Contribution and license information.
- Explicit statement that public suite scores are not full NVIQ certification.

- [ ] **Step 2: Add Apache-2.0 license and CI**

CI matrix: Python 3.11 and 3.12, install `.[dev]`, run `pytest -q`.

- [ ] **Step 3: Add architecture and sample report docs**

`examples/sample-report.md` must be clearly labeled as illustrative fixture output, not AMD hardware performance data.

- [ ] **Step 4: Run full verification**

Run: `python -m pytest -q`
Expected: all tests PASS.

Run: `python -m compileall -q src`
Expected: exit code 0.

Run: `python -m nviq_lemonade.cli --help` with `PYTHONPATH=src`.
Expected: command help lists `doctor` and `run`.

### Task 6: Submission branch review

**Files:** No new files unless verification finds a defect.

- [ ] **Step 1: Inspect repository for private-NVIQ leakage**

Search for private paths/names that should not be present: private scorer source, Reliability Audit implementation, remediation registry, private cases, credentials, tokens.

- [ ] **Step 2: Verify every challenge claim against implementation**

Do not claim live AMD GPU/NPU measurements until they have actually been captured on such hardware. It is valid to claim Lemonade API integration and telemetry capture capability after fixture + protocol tests pass.

- [ ] **Step 3: Open pull request from `dev/lemonade-foundation` to `main`**

PR title: `feat: launch NVIQ × Lemonade open evaluation foundation`

PR body summarizes architecture, public/private IP boundary, tests, and exact local Lemonade commands for live validation.