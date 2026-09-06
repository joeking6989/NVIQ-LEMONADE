# NVIQ × Lemonade 🍋

**Open cognitive + performance evaluation for local AI through Lemonade Server.**

NVIQ × Lemonade is a public Noct-Tech project built for the **AMD Lemonade Developer Challenge**. It connects to a locally running Lemonade Server, discovers installed models, runs transparent cognitive-behavior probes, captures Lemonade performance/system telemetry, and produces reproducible JSON + Markdown reports.

The project explores a simple question:

> **When a model runs locally, can we evaluate what it understands and preserves — not just how fast it generates tokens?**

## What it does

```text
NVIQ × Lemonade
      |
      +--> discovers downloaded Lemonade models
      +--> runs local chat probes through /v1/chat/completions
      +--> evaluates three open cognitive-behavior families
      +--> captures /v1/stats + /v1/system-info telemetry
      +--> writes report.json + report.md
```

The initial open suite covers:

- **Context Integrity** — does important information survive summarization/transformation?
- **Prior-Contamination Resistance** — can current evidence override an incorrect historical prior?
- **Confidence Discipline** — does the model preserve uncertainty when evidence is insufficient?

These are deliberately transparent public rules. They are **not** the proprietary full NVIQ scoring engine or a Noct-Tech NVIQ certification.

## Why Lemonade

Lemonade provides a local-first AI runtime with an OpenAI-compatible API plus local lifecycle and telemetry endpoints. NVIQ × Lemonade uses that interface to evaluate model behavior and execution characteristics through the same local runtime surface.

Current v0.1 API surface:

| Lemonade endpoint | Use |
|---|---|
| `GET /v1/health` | server status/version |
| `GET /v1/models` | downloaded model discovery |
| `POST /v1/chat/completions` | benchmark inference |
| `GET /v1/stats` | last-request performance telemetry |
| `GET /v1/system-info` | host/device information |

Lemonade Server documentation: https://lemonade-server.ai/docs/

AMD Lemonade Developer Challenge: https://www.amd.com/en/developer/resources/technical-articles/2026/join-the-lemonade-developer-challenge.html

## Quick start

### 1. Install and start Lemonade

Install Lemonade Server for your platform using the official guide:

https://lemonade-server.ai/docs/guide/install/

By default Lemonade serves locally on:

```text
http://127.0.0.1:13305
```

Install/download at least one model in Lemonade before running the suite.

### 2. Install NVIQ × Lemonade

```bash
git clone https://github.com/joeking6989/NVIQ-LEMONADE.git
cd NVIQ-LEMONADE
python -m pip install -e '.[dev]'
```

### 3. Check the local runtime

```bash
nviq-lemonade doctor
```

Example shape:

```text
Lemonade: ok (version 9.x)
Base URL: http://127.0.0.1:13305
Downloaded models: 2
  - Model-A [llamacpp]
  - Model-B [ryzenai-llm]
```

### 4. Run the open suite

```bash
nviq-lemonade run \
  --model YOUR_DOWNLOADED_MODEL_ID \
  --output-dir out/my-model
```

Outputs:

```text
out/my-model/
├── report.json
└── report.md
```

## Configuration

Use a different Lemonade server:

```bash
export LEMONADE_BASE_URL='http://127.0.0.1:13305'
```

If your Lemonade instance requires authentication:

```bash
export LEMONADE_API_KEY='your-local-api-key'
```

Or pass values explicitly:

```bash
nviq-lemonade \
  --base-url http://127.0.0.1:13305 \
  --api-key "$LEMONADE_API_KEY" \
  run --model YOUR_MODEL
```

## Evaluation methodology

The public cases live in [`cases/v0.1/public.json`](cases/v0.1/public.json). Every case declares its evaluation rule and expected observable evidence.

### 1. Context Integrity

The model receives multiple decision-relevant facts and must transform the context without losing any required fact. The public evaluator checks that all declared facts remain observable in the response.

### 2. Prior-Contamination Resistance

The model receives a historical prior that conflicts with a current direct observation. The evaluator checks that the response follows the current evidence.

### 3. Confidence Discipline

The model receives explicitly insufficient/contradictory evidence. The evaluator checks that the answer communicates uncertainty rather than manufacturing certainty.

The implementation is intentionally easy to audit in [`src/nviq_lemonade/evaluation.py`](src/nviq_lemonade/evaluation.py).

## Report contents

A run records:

- selected Lemonade model metadata;
- Lemonade server status/version;
- local system/device information when exposed by the server;
- the model response for each public case;
- transparent pass/fail evidence;
- wall-clock latency per case;
- Lemonade `/v1/stats` data when available;
- aggregate public-suite pass rate.

See [`examples/sample-report.md`](examples/sample-report.md) for an **illustrative fixture report**. It is intentionally not presented as real AMD hardware benchmark data.

## Architecture

```text
cases/v0.1/public.json
          |
          v
   Benchmark Runner
     /          \
    v            v
Lemonade       Public evaluator
Server              |
    |                |
    +--- telemetry --+
          |
          v
 report.json + report.md
```

More detail: [`docs/architecture.md`](docs/architecture.md)

## NVIQ IP boundary

Noct-Tech's canonical **NVIQ** project remains private. This public repository does **not** copy or publish:

- the canonical NVIQ scoring engine;
- proprietary benchmark cases or datasets;
- NVIQ Reliability Audit implementation;
- private remediation logic;
- unreleased research architecture.

NVIQ × Lemonade is a separately authored open-source integration and public evaluation suite designed to be useful on its own.

## Development

Run the tests:

```bash
python -m pytest -q
```

Compile-check the package:

```bash
python -m compileall -q src
```

The tests use an in-process Lemonade-compatible HTTP fixture, so CI does **not** require a GPU, NPU, model download, or live Lemonade installation.

## Status

**v0.1 foundation:**

- [x] Lemonade health/model discovery
- [x] OpenAI-compatible chat integration
- [x] Optional Lemonade request telemetry
- [x] Local system/device metadata capture
- [x] Three transparent public cognitive-evaluation families
- [x] JSON + Markdown reports
- [x] Hardware-independent automated tests
- [ ] Published real-device comparison results
- [ ] Recorded AMD challenge demo
- [ ] Expanded local-model comparison matrix

Real hardware results will only be published after they are actually measured; fixture data is never represented as AMD performance data.

## License

Apache License 2.0. See [`LICENSE`](LICENSE).

---

**Noct-Tech — NVIQ × Lemonade**
