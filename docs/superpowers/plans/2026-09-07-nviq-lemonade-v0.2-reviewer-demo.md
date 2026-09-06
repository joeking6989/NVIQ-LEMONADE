# NVIQ × Lemonade v0.2 Reviewer Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reviewer-ready multi-model NVIQ × Lemonade demo with real Lemonade telemetry, deterministic comparison, static HTML reporting, one-command demo UX, and release/community assets.

**Architecture:** Extend the existing provider-neutral public runner rather than changing evaluation semantics. Each model produces the existing report shape plus v0.2 telemetry aggregates and HTML; `comparison.py` orchestrates multiple independent runs and creates a comparison object. The CLI exposes `compare` and `demo` as thin orchestration layers.

**Tech Stack:** Python 3.11+, standard library only at runtime, pytest for development, Lemonade Server HTTP API.

**Spec:** `docs/superpowers/specs/2026-09-07-nviq-lemonade-v0.2-reviewer-demo-design.md`

## Global Constraints

- Keep the canonical private NVIQ scorer, proprietary benchmark cases/datasets, Reliability Audit, remediation registry, and unreleased research out of this repository.
- Runtime dependencies remain standard-library-only.
- Unsupported Lemonade telemetry is absent/null; never synthesize hardware measurements.
- Static HTML contains no remote scripts, remote fonts, or external runtime dependencies.
- Fixture/sample data must be visibly labelled illustrative and never described as AMD hardware data.
- Preserve `run` and `doctor` compatibility.

---

### Task 1: Lemonade system telemetry

**Files:**
- Modify: `src/nviq_lemonade/client.py`
- Modify: `tests/http_fixture.py`
- Modify: `tests/test_client.py`

**Interfaces:**
- Produces: `LemonadeClient.system_stats() -> dict | None`

- [ ] Write a failing client test asserting `GET /v1/system-stats` is parsed.
- [ ] Run the focused test and confirm it fails because `system_stats` does not exist.
- [ ] Add fixture endpoint and minimal client method using existing optional endpoint behavior.
- [ ] Run client tests and confirm green.

### Task 2: Per-model telemetry aggregation

**Files:**
- Modify: `src/nviq_lemonade/runner.py`
- Modify: `tests/test_runner.py`

**Interfaces:**
- Produces: `report["performance"]` with available aggregate metrics.
- Adds: `result["system_stats"]` per case.

- [ ] Write failing tests for mean TTFT/TPS/wall time, token totals, and peak sampled CPU/GPU/VRAM/NPU.
- [ ] Verify failures are due to missing v0.2 performance output.
- [ ] Implement numeric-only aggregation; ignore missing/non-numeric values.
- [ ] Preserve existing v0.1 fields and run runner tests green.

### Task 3: Multi-model comparison

**Files:**
- Create: `src/nviq_lemonade/comparison.py`
- Create: `tests/test_comparison.py`

**Interfaces:**
- Produces: `compare_models(client, models: list[str], cases: list[dict]) -> dict`
- Produces comparison schema `0.2` with `models`, `ranking`, `best_behavioral_model`, and metadata.

- [ ] Write failing tests with deterministic fake per-model responses/telemetry.
- [ ] Verify module/function missing.
- [ ] Implement sequential independent `run_suite` calls.
- [ ] Rank by pass rate desc, mean TPS desc when available, mean wall time asc.
- [ ] Verify comparison tests green.

### Task 4: Static HTML reports

**Files:**
- Create: `src/nviq_lemonade/html_reporting.py`
- Modify: `src/nviq_lemonade/reporting.py`
- Modify: `tests/test_reporting.py`
- Create: `tests/test_html_reporting.py`

**Interfaces:**
- Produces: `single_report_html(report: dict) -> str`
- Produces: `comparison_html(comparison: dict) -> str`
- Changes: `write_report(...) -> tuple[Path, Path, Path]`
- Produces: `write_comparison(...) -> tuple[Path, Path, Path]`

- [ ] Write failing tests for HTML summary content and HTML escaping.
- [ ] Implement dependency-free HTML renderers using `html.escape`.
- [ ] Extend report writer and add comparison JSON/Markdown/HTML writer.
- [ ] Run reporting tests green.

### Task 5: Compare and one-command demo CLI

**Files:**
- Modify: `src/nviq_lemonade/cli.py`
- Modify: `tests/test_cli.py`

**Interfaces:**
- Adds: `compare --model MODEL [--model MODEL...]`
- Adds: `demo [--model MODEL...] [--max-models N]`

- [ ] Write parser/selection tests first.
- [ ] Implement comparison execution and per-model report directories.
- [ ] Implement demo model discovery with deterministic max-model selection.
- [ ] Ensure no-model case returns a concise actionable error.
- [ ] Run CLI tests green.

### Task 6: Exact verification entrypoint and CI hygiene

**Files:**
- Create: `scripts/verify.py`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- `python scripts/verify.py` runs pytest then compileall and returns nonzero on failure.

- [ ] Add a subprocess-focused verification test if practical; otherwise validate script in the full local gate.
- [ ] Keep GitHub workflow minimal and call the exact verification entrypoint after installation.
- [ ] Run `python scripts/verify.py` locally.

### Task 7: Reviewer/demo/release documentation

**Files:**
- Modify: `README.md`
- Create: `docs/reviewer-walkthrough.md`
- Create: `docs/demo-script.md`
- Create: `docs/discord-post.md`
- Create: `results/README.md`
- Create: `RELEASE_NOTES_v0.2.0.md`
- Modify: `pyproject.toml`

**Interfaces:**
- Version becomes `0.2.0`.

- [ ] Put `demo` quick start and reviewer value proposition near README top.
- [ ] Document exact measured-results provenance requirements.
- [ ] Prepare a truthful 2–3 minute recording script and ready-to-paste Discord post.
- [ ] Add release notes and version bump.

### Task 8: End-to-end fixture comparison and final verification

**Files:**
- Create or modify fixture tests as needed under `tests/`.

- [ ] Run the full pytest suite.
- [ ] Run compileall.
- [ ] Execute fixture-backed comparison/demo path and verify JSON/Markdown/HTML artifacts.
- [ ] Scan repository changes for secrets, private NVIQ code, unsupported performance claims, and placeholders.
- [ ] Open a PR into `main`; merge only after the branch is locally green and the diff review is clean. Hosted Actions runner provisioning is tracked separately from code correctness if GitHub again assigns no runner.
