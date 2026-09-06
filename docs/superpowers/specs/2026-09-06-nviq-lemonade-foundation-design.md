# NVIQ × Lemonade Foundation Design

## Purpose

NVIQ-LEMONADE is the public, open-source local-AI evaluation companion to Noct-Tech's private NVIQ system. It demonstrates a genuine Lemonade integration for the AMD Lemonade Developer Challenge while preserving a strict IP boundary: the private canonical NVIQ scorer, proprietary benchmark corpus, commercial Reliability Audit logic, and unreleased research are not copied into this repository.

The public project must stand on its own. A reviewer should be able to clone it, point it at a running Lemonade Server, discover locally installed models, run an open evaluation suite, capture runtime telemetry, and produce a reproducible report without access to the private NVIQ repository.

## Product thesis

Local AI evaluation should measure more than raw throughput. NVIQ × Lemonade combines model-quality probes with Lemonade's local runtime and hardware telemetry so developers can compare both cognitive behavior and execution characteristics on their own machine.

## Public/private boundary

### Public in NVIQ-LEMONADE

- Lemonade HTTP client and model discovery.
- Open, independently authored benchmark cases suitable for public demonstration.
- Transparent public scoring rules for those cases.
- Runtime telemetry capture from Lemonade's public endpoints.
- Reproducible JSON and Markdown reports.
- CLI, tests, examples, documentation, CI, and open-source license.

### Remains private in NVIQ

- Canonical NVIQ scoring engine and hard-gate logic.
- Proprietary benchmark cases and datasets.
- Commercial Reliability Audit implementation and remediation registry.
- Private research artifacts, unreleased evaluators, and internal product architecture.

No source file is copied from the private NVIQ repository. Shared concepts may be represented only through newly authored public cases and clearly documented public rules.

## v0.1 scope

The first milestone is intentionally small but real:

1. Connect to Lemonade Server at a configurable base URL, defaulting to `http://127.0.0.1:13305`.
2. Verify server health with `GET /v1/health`.
3. Discover downloaded models with `GET /v1/models`.
4. Execute chat probes through `POST /v1/chat/completions`.
5. Capture Lemonade request statistics with `GET /v1/stats` when available.
6. Capture host/device information with `GET /v1/system-info` when available.
7. Run an open benchmark subset covering three NVIQ-inspired public dimensions:
   - Context Integrity
   - Prior-Contamination Resistance
   - Confidence Discipline
8. Produce a machine-readable JSON report and a human-readable Markdown report.
9. Work without third-party Python runtime dependencies; use Python 3.11+ standard library for the core package.
10. Include tests that run without Lemonade hardware by using a local HTTP fixture server.

## Architecture

```text
CLI
 |
 v
Benchmark Runner -----------------------+
 |                                      |
 +--> Public benchmark cases            |
 |                                      |
 +--> LemonadeClient -------------------+
       |                                 |
       +--> /v1/health                   |
       +--> /v1/models                   |
       +--> /v1/chat/completions         |
       +--> /v1/stats                    |
       +--> /v1/system-info              |
                                         v
                                Evaluation records
                                         |
                                         v
                                 Public scorer
                                         |
                                         v
                              JSON + Markdown report
```

## Components

### `src/nviq_lemonade/client.py`

A small standard-library HTTP client. It owns URL construction, JSON transport, optional API-key authentication, timeout handling, HTTP error normalization, and endpoint methods. It does not score outputs.

Public interface:

- `LemonadeClient(base_url: str, api_key: str | None = None, timeout_s: float = 60.0)`
- `health() -> dict`
- `models() -> list[dict]`
- `chat(model: str, messages: list[dict], *, temperature: float = 0.0) -> dict`
- `stats() -> dict | None`
- `system_info() -> dict | None`

Optional telemetry endpoints return `None` on 404 so older Lemonade versions remain usable. Connection failures and non-optional API failures raise `LemonadeError` with an actionable message.

### `src/nviq_lemonade/cases.py`

Defines the public benchmark contract and loads versioned JSON cases from `cases/v0.1/public.json`.

Each case contains:

- stable `case_id`
- public `family`
- system/user messages
- evaluation rule identifier
- expected evidence needed by that rule

No hidden/private benchmark content is imported.

### `src/nviq_lemonade/evaluation.py`

Transparent deterministic evaluation rules for the public cases. The v0.1 rules intentionally score observable response properties rather than claiming equivalence to private NVIQ scoring.

Rules:

- `contains_required_facts`: required facts must survive context transformation.
- `rejects_false_prior`: response must choose current evidence over a supplied contradictory historical prior.
- `confidence_matches_evidence`: response must avoid unsupported certainty and include an uncertainty marker when evidence is explicitly incomplete.

Each case yields `pass: bool`, `score: 0.0 | 1.0`, and a concise evidence explanation.

### `src/nviq_lemonade/runner.py`

Orchestrates one model run. It records wall-clock latency, calls Lemonade, extracts assistant text, obtains optional Lemonade stats, evaluates each case, and returns a serializable run report.

### `src/nviq_lemonade/reporting.py`

Writes deterministic JSON and Markdown reports. Reports include project/version metadata, Lemonade health/system information, selected model metadata, per-case outcomes, aggregate pass rate, wall-clock latency, and Lemonade stats when available.

### `src/nviq_lemonade/cli.py`

Commands:

- `nviq-lemonade doctor` — server health and local model inventory.
- `nviq-lemonade run --model MODEL --output-dir PATH` — execute the public v0.1 suite.

The CLI reads `LEMONADE_BASE_URL` and `LEMONADE_API_KEY`; command-line base URL overrides the environment.

## Data flow

For each case:

1. Runner sends the case messages to Lemonade chat completions.
2. Lemonade loads/routes the named local model and returns an OpenAI-compatible response.
3. Runner extracts `choices[0].message.content` and records elapsed wall time.
4. Runner requests `/v1/stats` and attaches the returned Lemonade performance data if supported.
5. Public evaluator applies the case's declared deterministic rule.
6. Result is appended to the run report.
7. Reporting writes complete JSON plus a concise Markdown comparison surface.

## Error handling

- Unreachable server: fail with `LemonadeError` and point to the configured base URL.
- Unknown model / inference HTTP error: preserve HTTP status and server error message.
- Malformed JSON: fail explicitly; never fabricate a completion or metric.
- Missing completion content: fail the case with a transport/protocol error rather than scoring empty text as model behavior.
- `/v1/stats` or `/v1/system-info` absent: continue without that optional telemetry and record it as unavailable.
- Empty downloaded-model inventory: `doctor` succeeds but explains that a model must be installed before `run`.

## Testing strategy

All core behavior is testable without AMD hardware or a live Lemonade install.

- Unit tests for evaluation rules.
- Local HTTP fixture server tests for health, model discovery, chat, optional telemetry, auth header behavior, and normalized failures.
- Runner integration test using the fixture server.
- Reporting tests for deterministic JSON/Markdown output.
- CLI smoke test for `doctor` against the fixture server.

Production code follows test-first red/green development.

## Repository structure

```text
NVIQ-LEMONADE/
├── .github/workflows/ci.yml
├── cases/v0.1/public.json
├── docs/
│   ├── architecture.md
│   └── superpowers/
│       ├── specs/
│       └── plans/
├── examples/
│   └── sample-report.md
├── src/nviq_lemonade/
│   ├── __init__.py
│   ├── cases.py
│   ├── cli.py
│   ├── client.py
│   ├── errors.py
│   ├── evaluation.py
│   ├── reporting.py
│   └── runner.py
├── tests/
├── LICENSE
├── README.md
└── pyproject.toml
```

## License

Apache License 2.0. It satisfies the challenge's open-source requirement while providing an explicit patent grant appropriate for a developer-facing integration project.

## Success criteria for the AMD application milestone

The repository is application-ready when:

- It is public under Apache-2.0.
- `python -m pytest` passes locally.
- `nviq-lemonade doctor` can interrogate a Lemonade-compatible fixture and is documented for a real server.
- `nviq-lemonade run` executes all public cases against a named model.
- JSON and Markdown reports are generated reproducibly.
- README explains the problem, architecture, Lemonade integration, benchmark methodology, privacy/local-AI value, and how to reproduce results.
- CI runs the test suite on Python 3.11 and 3.12.
- No private NVIQ source, proprietary scoring logic, secrets, or private benchmark corpus appears in the public repository.

## Explicit non-goals for v0.1

- Releasing the private NVIQ scorer.
- Claiming the public score is a full NVIQ certification or Reliability Audit.
- Building a hosted SaaS backend.
- Building a large frontend before the CLI/report workflow is verified.
- Requiring AMD-specific hardware to run the software.

These can be expanded after the first challenge-ready milestone is working.