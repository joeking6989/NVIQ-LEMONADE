# Architecture

NVIQ × Lemonade is deliberately split into two concerns:

1. **Lemonade execution + telemetry** — the public client discovers local models, sends OpenAI-compatible chat requests, and captures Lemonade runtime/system metadata.
2. **Open evaluation** — a small transparent suite measures observable response behavior using public deterministic rules.

```text
public cases
    |
    v
Benchmark Runner ---> Lemonade Server ---> local model/runtime
    |                       |
    |                       +--> /v1/stats
    |                       +--> /v1/system-info
    v
public evaluator
    |
    v
JSON + Markdown report
```

## IP boundary

This repository is **not** a source mirror of Noct-Tech's private NVIQ repository. The canonical NVIQ scorer, private cases/datasets, Reliability Audit implementation, remediation registry, and unreleased research remain private.

The public suite is independently authored and intentionally transparent. It demonstrates how NVIQ-inspired evaluation concepts can be applied to local models through Lemonade without publishing the proprietary NVIQ product.

## Lemonade protocol surface

The v0.1 integration uses:

- `GET /v1/health`
- `GET /v1/models`
- `POST /v1/chat/completions`
- `GET /v1/stats` (optional)
- `GET /v1/system-info` (optional)

The default base URL is `http://127.0.0.1:13305`. An API key can be supplied through `LEMONADE_API_KEY` or `--api-key`.

## Public benchmark families

### Context Integrity

Checks whether decision-relevant details survive a constrained transformation rather than being silently dropped.

### Prior-Contamination Resistance

Checks whether current direct evidence can override a contradictory historical prior.

### Confidence Discipline

Checks whether a response preserves uncertainty when the supplied evidence is explicitly insufficient or contradictory.

These public rules are intentionally readable in `src/nviq_lemonade/evaluation.py`. They are **not** the private NVIQ scoring engine.
