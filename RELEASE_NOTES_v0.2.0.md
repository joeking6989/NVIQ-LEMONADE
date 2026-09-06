# NVIQ × Lemonade v0.2.0 — Reviewer Demo

v0.2.0 turns the initial Lemonade integration into a reviewer-ready local-AI comparison tool.

## Highlights

- **One-command demo:** `nviq-lemonade demo`
- **Multi-model comparison:** `nviq-lemonade compare --model ...`
- **Behavior-first ranking:** public-suite reliability outranks raw throughput
- **Expanded Lemonade telemetry:** `/v1/stats` plus `/v1/system-stats`
- **Performance aggregation:** TTFT, tokens/sec, token totals, wall time, CPU/GPU/NPU/VRAM samples
- **Static visual dashboards:** dependency-free `report.html` and `comparison.html`
- **Reviewer bundle:** per-model JSON/Markdown/HTML plus comparison artifacts
- **Reproducible verification:** `python scripts/verify.py`
- **Measurement provenance policy:** clear separation between fixtures and real device results

## Compatibility

- Python 3.11+
- Runtime dependencies: Python standard library only
- Lemonade default endpoint: `http://127.0.0.1:13305`

## Verification

```bash
python -m pip install -e '.[dev]'
python scripts/verify.py
```

## Important result-integrity note

No fixture result is a hardware benchmark. Publish real model/device measurements only with the provenance described in `results/README.md`.

## NVIQ boundary

This release remains a separately authored public integration and evaluation suite. It does not publish the private canonical NVIQ scoring engine, proprietary cases/datasets, Reliability Audit implementation, private remediation logic, or unreleased Noct-Tech research.
