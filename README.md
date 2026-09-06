# NVIQ × Lemonade 🍋

**Behavior + performance evaluation for local AI through Lemonade Server.**

NVIQ × Lemonade is an open-source Noct-Tech project built for the **AMD Lemonade Developer Challenge**. It evaluates locally running models through Lemonade's real API surface, then places **behavioral reliability and hardware/runtime telemetry in the same report**.

> **The question:** when a model runs locally, can we measure what it preserves, how it reacts to new evidence, and whether it respects uncertainty — not only how fast it emits tokens?

## Reviewer quick path — one command

With Lemonade Server running and at least one local model downloaded:

```bash
python -m pip install -e '.[dev]'
nviq-lemonade demo --output-dir out/demo
```

Then open:

```text
out/demo/comparison.html
```

`demo` automatically discovers downloaded **local** Lemonade models, evaluates up to two by default, captures runtime telemetry, and creates a self-contained visual comparison bundle.

```text
out/demo/
├── comparison.json
├── comparison.md
├── comparison.html
└── models/
    ├── <model-a>/
    │   ├── report.json
    │   ├── report.md
    │   └── report.html
    └── <model-b>/
        ├── report.json
        ├── report.md
        └── report.html
```

No web app, cloud service, JavaScript package, external font, or hosted dashboard is required to view the HTML report.

### UI preview

![NVIQ × Lemonade fixture comparison dashboard](docs/assets/fixture-comparison-dashboard.png)

> **Illustrative fixture UI preview — not hardware benchmark data.** The screenshot is generated from the deterministic test fixture so reviewers can see the report surface without installing a model. Real measurements are only published with the provenance defined in `results/README.md`.

## Why this is different

Most local-AI benchmarking stops at throughput, latency, and memory. NVIQ × Lemonade deliberately shows two dimensions together:

| Dimension | Examples |
|---|---|
| **Behavior** | context integrity, prior-contamination resistance, confidence discipline |
| **Runtime** | time-to-first-token, tokens/sec, wall time, CPU/GPU/NPU utilization, VRAM |

The comparison ordering is intentionally **behavior first, speed second**. A faster model does not outrank a more behaviorally reliable model solely because it generates more tokens per second.

This ordering is a transparent public-demo heuristic. It is **not** Noct-Tech's proprietary canonical NVIQ scorer or a Noct-Tech certification.

## What v0.2 does

```text
                       NVIQ × Lemonade
                              |
                +-------------+-------------+
                |                           |
        public evaluation              Lemonade runtime
                |                           |
   +------------+------------+     +--------+----------------+
   |            |            |     |        |        |       |
 Context     Prior         Confidence  models   inference  telemetry
 Integrity  Resistance    Discipline  /v1/...  chat API   stats/system
   |            |            |          |        |        |
   +------------+------------+----------+--------+--------+
                              |
                    behavior + performance
                              |
               JSON + Markdown + static HTML
```

The open suite currently covers:

- **Context Integrity** — does decision-relevant information survive summarization/transformation?
- **Prior-Contamination Resistance** — can current direct evidence override an incorrect historical prior?
- **Confidence Discipline** — does the model preserve uncertainty when evidence is insufficient or contradictory?

The rules and cases are deliberately readable and auditable.

## Lemonade integration

The project calls documented Lemonade endpoints directly:

| Lemonade endpoint | Use |
|---|---|
| `GET /v1/health` | server status/version |
| `GET /v1/models` | local model discovery |
| `POST /v1/chat/completions` | benchmark inference |
| `GET /v1/stats` | post-inference TTFT/token throughput/token counts |
| `GET /v1/system-stats` | sampled CPU/RAM/GPU/VRAM/NPU utilization |
| `GET /v1/system-info` | host/device information |

Official Lemonade docs: https://lemonade-server.ai/docs/

AMD Lemonade Developer Challenge: https://www.amd.com/en/developer/resources/technical-articles/2026/join-the-lemonade-developer-challenge.html

## Install

### 1. Install and start Lemonade Server

Follow the official installation guide:

https://lemonade-server.ai/docs/guide/install/

The default local server is:

```text
http://127.0.0.1:13305
```

Download at least one local model in Lemonade.

### 2. Install NVIQ × Lemonade

```bash
git clone https://github.com/joeking6989/NVIQ-LEMONADE.git
cd NVIQ-LEMONADE
python -m pip install -e '.[dev]'
```

### 3. Inspect the runtime

```bash
nviq-lemonade doctor
```

### 4. Run the reviewer demo

```bash
nviq-lemonade demo --output-dir out/demo
```

To evaluate more auto-discovered models:

```bash
nviq-lemonade demo --max-models 4 --output-dir out/demo
```

To explicitly control the models:

```bash
nviq-lemonade demo \
  --model MODEL_A \
  --model MODEL_B \
  --output-dir out/demo
```

## Commands

### Single model

```bash
nviq-lemonade run \
  --model YOUR_DOWNLOADED_MODEL_ID \
  --output-dir out/my-model
```

### Explicit comparison

```bash
nviq-lemonade compare \
  --model MODEL_A \
  --model MODEL_B \
  --output-dir out/compare
```

### Configuration

```bash
export LEMONADE_BASE_URL='http://127.0.0.1:13305'
export LEMONADE_API_KEY='optional-local-api-key'
```

Or pass values explicitly:

```bash
nviq-lemonade \
  --base-url http://127.0.0.1:13305 \
  --api-key "$LEMONADE_API_KEY" \
  demo
```

## Telemetry and comparison methodology

Every case captures:

- model response;
- deterministic public pass/fail evidence;
- wall-clock request latency;
- Lemonade `/v1/stats` after inference, when available;
- Lemonade `/v1/system-stats` sample after inference, when available.

The per-model report derives only from numeric values Lemonade actually exposes:

- mean time to first token;
- mean tokens per second;
- total input/output tokens;
- mean wall-clock latency;
- peak sampled CPU utilization;
- peak sampled memory usage;
- peak sampled GPU utilization;
- peak sampled VRAM usage;
- peak sampled NPU utilization.

Unsupported telemetry stays unavailable (`null` / `—`). **NVIQ × Lemonade never invents a hardware metric.**

Comparison ordering is deterministic:

1. higher public-suite pass rate;
2. higher mean tokens/sec when available;
3. lower mean wall-clock latency;
4. model ID as a deterministic final tie-break.

## Public evaluation methodology

Cases live in [`cases/v0.1/public.json`](cases/v0.1/public.json). The case schema remains intentionally simple so developers can inspect exactly what is being tested.

The evaluator implementation is in [`src/nviq_lemonade/evaluation.py`](src/nviq_lemonade/evaluation.py).

### Context Integrity

The model receives multiple decision-relevant facts and must transform the context without dropping any configured required fact.

### Prior-Contamination Resistance

The model receives a historical prior that conflicts with a current direct observation. Current evidence must win.

### Confidence Discipline

The model receives insufficient or contradictory evidence. It must express uncertainty rather than manufacture certainty.

## Static visual reports

`report.html` and `comparison.html` are generated by the Python standard library only. They are:

- self-contained;
- responsive;
- dependency-free;
- safe against raw model text being interpreted as HTML;
- viewable directly from disk.

The comparison dashboard deliberately makes behavioral score, tokens/sec, TTFT, wall time, and available accelerator telemetry visible together.

## Real measurement policy

Fixture tests prove the software path; they are **not hardware benchmarks**.

Real model/hardware results are only publishable when produced by a live Lemonade run and accompanied by provenance. See [`results/README.md`](results/README.md).

No fixture result is represented as AMD performance data.

## Architecture

See [`docs/architecture.md`](docs/architecture.md).

Reviewer walkthrough: [`docs/reviewer-walkthrough.md`](docs/reviewer-walkthrough.md)

Recording script: [`docs/demo-script.md`](docs/demo-script.md)

## NVIQ IP boundary

Noct-Tech's canonical **NVIQ** project remains private. This public repository does **not** copy or publish:

- the canonical NVIQ scoring engine;
- proprietary benchmark cases or datasets;
- NVIQ Reliability Audit implementation;
- private remediation logic;
- unreleased research architecture.

NVIQ × Lemonade is a separately authored open-source integration and public evaluation suite that is fully useful without access to the private repository.

## Development and verification

Exact verification gate:

```bash
python scripts/verify.py
```

Equivalent manual commands:

```bash
python -m pytest -q
python -m compileall -q src
```

Tests use an in-process Lemonade-compatible HTTP fixture, so verification does not require a GPU, NPU, model download, or live Lemonade installation.

### GitHub Actions note

The repository includes a minimal Actions workflow using the same `scripts/verify.py` gate. A previous GitHub-hosted run failed before any runner was assigned or any workflow step executed; that is a hosted runner/account provisioning condition rather than a Python test failure. Local verification remains the source of evidence when GitHub does not provision a runner.

## Challenge/demo material

- [`docs/reviewer-walkthrough.md`](docs/reviewer-walkthrough.md) — fast reviewer path
- [`docs/demo-script.md`](docs/demo-script.md) — exact 2–3 minute recording script
- [`docs/discord-post.md`](docs/discord-post.md) — ready-to-post `#AMDDevChallenge` copy
- [`RELEASE_NOTES_v0.2.0.md`](RELEASE_NOTES_v0.2.0.md) — release notes

## Status

**v0.2 reviewer demo:**

- [x] Lemonade local model discovery
- [x] OpenAI-compatible chat integration
- [x] `/v1/stats` request telemetry
- [x] `/v1/system-stats` CPU/GPU/NPU sampling
- [x] `/v1/system-info` host/device capture
- [x] Three transparent cognitive-behavior families
- [x] Single-model JSON + Markdown + HTML reports
- [x] Behavior-first multi-model comparison
- [x] One-command reviewer demo
- [x] Hardware-independent automated tests
- [x] Exact local/CI verification gate
- [x] Recording/community/release documentation
- [ ] Publish first provenance-complete real-device comparison
- [ ] Upload a recorded live-Lemonade demo

The final two items require a real Lemonade runtime/hardware session and a video/community account; the repository is prepared so those outputs can be created without further engineering changes.

## License

Apache License 2.0. See [`LICENSE`](LICENSE).

---

**Noct-Tech — NVIQ × Lemonade**
