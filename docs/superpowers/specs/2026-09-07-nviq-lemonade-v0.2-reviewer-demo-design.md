# NVIQ × Lemonade v0.2 Reviewer Demo Design

## Goal

Turn the v0.1 public foundation into a reviewer-ready local-AI evaluation tool that makes Lemonade integration immediately visible: one-command model discovery/evaluation, multi-model comparison, runtime telemetry, and a static visual report that can be opened locally without a web service.

## Competition alignment

The v0.2 surface is optimized for the AMD Lemonade Developer Challenge criteria: community usefulness/clarity, technical depth, and creativity. It uses Lemonade's documented local interfaces rather than emulating them: `/v1/models`, `/v1/chat/completions`, `/v1/stats`, `/v1/system-stats`, `/v1/system-info`, and `/v1/health`.

## Public/private boundary

The canonical private NVIQ scorer, proprietary benchmark cases/datasets, Reliability Audit, remediation registry, and unreleased Noct-Tech research remain outside this repository. v0.2 continues to use only transparent public rules and public cases.

## Reviewer flows

### Fastest live flow

```bash
nviq-lemonade demo --output-dir out/demo
```

`demo` checks Lemonade, discovers downloaded local models, selects up to two by default, runs the public suite, and writes a reviewer bundle.

### Explicit comparison

```bash
nviq-lemonade compare \
  --model MODEL_A \
  --model MODEL_B \
  --output-dir out/compare
```

### Single-model flow

The existing `run` command remains supported and gains HTML output plus aggregate performance telemetry.

## Reviewer bundle

A comparison/demo output directory contains:

```text
out/demo/
  comparison.json
  comparison.md
  comparison.html
  models/
    <safe-model-id>/
      report.json
      report.md
      report.html
```

The HTML is static, self-contained, dependency-free, and contains no remote scripts or fonts.

## Telemetry model

Each case preserves the existing wall-clock measurement and the post-request `/v1/stats` snapshot. v0.2 also samples `/v1/system-stats` after each case when available. The report derives, from available numeric samples only:

- mean time to first token;
- mean tokens per second;
- total input/output tokens;
- mean wall-clock latency;
- peak sampled CPU utilization;
- peak sampled GPU utilization;
- peak sampled VRAM usage;
- peak sampled NPU utilization.

Unsupported telemetry remains `null`/absent rather than being guessed. Fixture results are always labelled fixture/illustrative and are never presented as AMD hardware measurements.

## Comparison model

A comparison ranks models by public-suite pass rate first, then mean tokens/sec when available, then lower mean wall time. This is explicitly a demo ordering heuristic, not the canonical NVIQ scorer.

Every comparison row preserves both behavioral and runtime dimensions so a faster model cannot silently hide a behavioral failure.

## Client changes

Add `LemonadeClient.system_stats()` using `GET /v1/system-stats` as an optional endpoint. Keep all existing error normalization and authentication behavior.

## New modules

- `comparison.py` — multi-model execution, aggregation, deterministic ranking.
- `html_reporting.py` — static single-model and comparison HTML rendering.

Existing `reporting.py` remains responsible for JSON/Markdown and calls the HTML renderer for the new third artifact.

## CLI

Commands after v0.2:

- `doctor`
- `run --model ...`
- `compare --model ... --model ...`
- `demo [--max-models 2] [--model ...]`

`demo` uses explicitly supplied models when provided; otherwise it chooses downloaded models returned by Lemonade, preserving server order and limiting to `--max-models`. It fails clearly when no downloaded model is available.

## CI and verification

The repository workflow remains valid GitHub Actions YAML and runs package install, pytest, and compile verification. The prior hosted Actions failure occurred before a runner was assigned (zero steps, runner id 0 on both Python matrix jobs and on retry), so it is treated as a runner/account provisioning condition rather than a code-test failure. v0.2 adds a single local verification entrypoint so the exact same quality gate can be run independently of hosted runner availability.

## Demo/release assets

Add:

- `scripts/verify.py` — install-independent verification of tests/compile when dependencies are present;
- `docs/reviewer-walkthrough.md` — 60-second evaluation path;
- `docs/demo-script.md` — 2–3 minute recording script with exact commands and claims;
- `docs/discord-post.md` — ready-to-post `#AMDDevChallenge` copy;
- `RELEASE_NOTES_v0.2.0.md` — release notes ready for GitHub Release creation.

The repository cannot manufacture real hardware data. `results/README.md` defines the provenance requirements for publishing future measured runs.

## Success criteria

1. Existing v0.1 tests remain green.
2. New tests cover system stats, aggregation, ranking, compare/demo selection, and HTML escaping/rendering.
3. A fixture-backed end-to-end comparison produces JSON, Markdown, and HTML.
4. `python -m compileall -q src` succeeds.
5. No secrets, private NVIQ source, or unsupported hardware claims are introduced.
6. README exposes a reviewer-first quick path in the first screenful.
