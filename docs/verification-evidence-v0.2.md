# v0.2 Verification Evidence

This document records the verification evidence for the NVIQ × Lemonade v0.2 reviewer-demo milestone.

## Fresh exact-source verification

After the final v0.2 implementation and documentation refinements, the committed branch source/test files were reconstructed in the local verification sandbox and checked against their GitHub blob SHAs. The exact verification gate was then executed against that source tree:

```bash
PYTHONPATH=src python scripts/verify.py
```

Result:

```text
[verify] pytest
....................                                                     [100%]
20 passed in 4.22s
[verify] compileall src
[verify] OK
```

The `PYTHONPATH=src` prefix is only required in the restricted verification sandbox because it cannot access the internet to fetch build dependencies for an editable install. The repository/CI path remains `python -m pip install -e '.[dev]'` followed by `python scripts/verify.py`.

The verified suite covers:

- Lemonade health/model discovery and authenticated client behavior;
- OpenAI-compatible chat execution;
- `/v1/stats` inference telemetry;
- `/v1/system-stats` host-resource sampling;
- Context Integrity, Prior-Contamination Resistance, and Confidence Discipline evaluation;
- telemetry aggregation with unavailable values preserved;
- behavior-first multi-model comparison;
- `doctor`, `run`, `compare`, and `demo` CLI paths;
- JSON, Markdown, and static HTML artifact generation;
- safe output-directory naming for arbitrary model IDs;
- HTML escaping of untrusted model/evidence text.

## Official Lemonade API contract check

The implementation was checked against the current Lemonade Server documentation for:

- `POST /v1/chat/completions`;
- `GET /v1/stats`;
- `GET /v1/system-stats`;
- `GET /v1/system-info`.

The v0.2 telemetry fields match the documented contracts:

### `/v1/stats`

- `time_to_first_token`
- `tokens_per_second`
- `input_tokens`
- `output_tokens`

### `/v1/system-stats`

- `cpu_percent`
- `memory_gb`
- `gpu_percent`
- `vram_gb`
- `npu_percent`

Unsupported GPU/VRAM/NPU values are permitted to be `null`; NVIQ × Lemonade preserves missing values rather than fabricating replacements.

## Host telemetry semantics

`/v1/system-stats` is a current host-resource snapshot. v0.2 samples it after each benchmark inference. Aggregate fields named `peak_*` in the machine-readable schema therefore mean the maximum observed value across those post-inference samples; public-facing reports explicitly label them **Max sampled** and state that they are not continuous in-request peaks.

## GitHub Actions infrastructure condition

GitHub-hosted Actions runs for this repository have repeatedly terminated before GitHub assigns a runner. The observed jobs have:

- `runner_id: 0`;
- empty runner name;
- zero workflow steps executed.

That state is an Actions runner/account provisioning condition. It is not evidence of a Python test, package-install, compile, or application failure because none of those steps execute.

The repository keeps the minimal Actions workflow in place so CI will use the same `python scripts/verify.py` gate as soon as GitHub provisions a runner.

## Measurement integrity

Fixture outputs demonstrate software behavior only. They are not represented as AMD hardware benchmark results. Real-device results require the provenance fields defined in `results/README.md`.
