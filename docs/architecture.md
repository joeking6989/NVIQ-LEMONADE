# Architecture

NVIQ × Lemonade v0.2 separates four concerns so each can be inspected and tested independently:

1. **Lemonade execution** — discover models and send OpenAI-compatible chat requests.
2. **Lemonade telemetry** — capture request performance, current system utilization, and host/device metadata.
3. **Open behavioral evaluation** — evaluate transparent public cases with deterministic public rules.
4. **Comparison/reporting** — preserve every per-model report, apply a transparent behavior-first ordering, and emit JSON, Markdown, and static HTML.

```text
public cases
    |
    v
Benchmark Runner -----------------> Lemonade Server -----------------> local model/runtime
    |                                    |                                  |
    |                                    +--> /v1/stats <--------------------+
    |                                    +--> /v1/system-stats
    |                                    +--> /v1/system-info
    v
public evaluator
    |
    +--> one model --> report.json / report.md / report.html
    |
    +--> many models
            |
            v
      comparison.py
            |
            v
 comparison.json / comparison.md / comparison.html
```

## Lemonade protocol surface

The v0.2 integration uses documented Lemonade interfaces:

- `GET /v1/health`
- `GET /v1/models`
- `POST /v1/chat/completions`
- `GET /v1/stats` (optional request-performance telemetry)
- `GET /v1/system-stats` (optional CPU/RAM/GPU/VRAM/NPU sample)
- `GET /v1/system-info` (optional host/device metadata)

The default base URL is `http://127.0.0.1:13305`. An API key can be supplied through `LEMONADE_API_KEY` or `--api-key`.

`/v1/stats` is read immediately after each inference so the model request remains the source of the captured request-performance snapshot. `/v1/system-stats` is then sampled for current host utilization. Unsupported optional telemetry remains unavailable rather than being inferred.

## Public behavioral layer

### Context Integrity

Checks whether decision-relevant details survive a constrained transformation rather than being silently dropped.

### Prior-Contamination Resistance

Checks whether current direct evidence can override a contradictory historical prior.

### Confidence Discipline

Checks whether a response preserves uncertainty when the supplied evidence is explicitly insufficient or contradictory.

These public rules are intentionally readable in `src/nviq_lemonade/evaluation.py`. They are **not** the private NVIQ scoring engine.

## Performance aggregation

`runner.py` derives only from numeric telemetry actually returned by Lemonade:

- mean TTFT;
- mean tokens/sec;
- input/output token totals;
- mean wall time;
- peak sampled CPU and memory;
- peak sampled GPU and VRAM;
- peak sampled NPU.

A missing metric remains `None` and renders as unavailable.

## Comparison ordering

`comparison.py` keeps each complete per-model report, extracts a compact comparison row, and orders models by:

1. higher public-suite pass rate;
2. higher mean tokens/sec when available;
3. lower mean wall-clock latency;
4. model ID as a deterministic final tie-break.

This is a public demonstration heuristic, not the canonical NVIQ scorer. Behavioral reliability is deliberately the first ordering dimension so throughput cannot silently mask a behavioral failure.

## Static report surface

`html_reporting.py` creates dependency-free HTML using the Python standard library. Model IDs, evidence, and other untrusted text are HTML-escaped. Reports include no remote scripts or fonts and can be opened directly from disk.

## IP boundary

This repository is **not** a source mirror of Noct-Tech's private NVIQ repository. The canonical NVIQ scorer, private cases/datasets, Reliability Audit implementation, remediation registry, and unreleased research remain private.

The public suite is independently authored and intentionally transparent. It demonstrates how NVIQ-inspired evaluation concepts can be applied to local models through Lemonade without publishing the proprietary NVIQ product.
