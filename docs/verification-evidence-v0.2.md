# v0.2 Verification Evidence

This document records the verification evidence for the NVIQ × Lemonade v0.2 reviewer-demo milestone.

## Local verification

Before the final documentation-only telemetry-label refinements, the complete v0.2 implementation was exercised with the repository verification path and produced:

- 17 automated tests passing;
- package compile check passing;
- CLI `doctor`, `run`, `compare`, and `demo` fixture paths exercised;
- generated JSON, Markdown, and HTML report artifacts;
- fixture comparison ranking verified as behavior-first;
- API-key handling and HTML escaping covered by tests.

The final changes after that run were documentation/presentation precision changes only: the README fixture-preview path and the wording used for post-inference host-resource samples.

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
