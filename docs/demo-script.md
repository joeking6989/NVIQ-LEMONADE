# AMD Lemonade Challenge Demo Script — 2–3 minutes

This script is designed for a **live Lemonade runtime**. Do not substitute fixture results while describing hardware performance.

## Shot 1 — 0:00–0:20 — Problem

**Screen:** repository README, then terminal.

**Narration:**

> Local AI benchmarks usually tell us how fast a model runs. NVIQ × Lemonade asks a second question: while it is running locally, how reliably does it preserve context, respond to new evidence, and respect uncertainty?

## Shot 2 — 0:20–0:40 — Lemonade discovery

Run:

```bash
nviq-lemonade doctor
```

**Narration:**

> The project talks directly to Lemonade Server. It discovers the locally available models and captures the host and device information Lemonade exposes.

Pause long enough for the Lemonade version and model list to be visible.

## Shot 3 — 0:40–1:30 — One-command demo

Run:

```bash
nviq-lemonade demo --output-dir out/demo
```

**Narration:**

> One command evaluates up to two downloaded local models. Every model receives the same transparent public probes. After each inference, NVIQ × Lemonade captures Lemonade's request performance statistics and available CPU, GPU, VRAM, and NPU telemetry.

Show the terminal's final `Behavioral leader` and `Open this report` lines.

## Shot 4 — 1:30–2:20 — Visual comparison

Open `out/demo/comparison.html`.

**Narration:**

> The output deliberately puts behavior and performance on the same screen. The ranking is behavior first and speed second, so a faster model cannot hide a behavioral failure behind a higher tokens-per-second number.

Point to pass rate, tokens/sec, TTFT, wall time, accelerator telemetry, and the behavior-first ranking statement. Then open one model's `report.html` and show the case-level evidence.

## Shot 5 — 2:20–2:45 — Open-source value

**Screen:** `src/nviq_lemonade/evaluation.py`, `cases/v0.1/public.json`, and `results/README.md`.

**Narration:**

> The public rules are intentionally simple enough to audit. Results are reproducible JSON, Markdown, and static HTML, and real hardware results are only published with provenance. The project is Apache-2.0 and runs entirely through the local Lemonade interface.

## Shot 6 — 2:45–3:00 — Close

**Narration:**

> NVIQ × Lemonade turns local inference benchmarking into local AI reliability benchmarking: what the model does, plus how the hardware runs it.

**Final screen:** repository URL and `comparison.html`.

## Recording checklist

- Use a real local Lemonade model.
- Keep terminal text large enough to read.
- Do not claim fixture data as AMD or device benchmark data.
- If a telemetry field is unavailable, leave the `—` visible and explain that the tool refuses to guess unsupported metrics.
- Keep the repository URL visible at the end.
