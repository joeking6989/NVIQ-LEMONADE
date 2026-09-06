# Reviewer Walkthrough — NVIQ × Lemonade v0.2

## 60-second path

Prerequisites: Lemonade Server running locally and at least one local model downloaded.

```bash
python -m pip install -e '.[dev]'
nviq-lemonade doctor
nviq-lemonade demo --output-dir out/demo
```

Open `out/demo/comparison.html`.

## What to look for

1. **Real Lemonade integration** — model discovery and inference use Lemonade's HTTP APIs rather than a bundled inference runtime.
2. **Behavior + performance together** — each model has a public cognitive-behavior pass rate next to Lemonade TTFT/tokens-per-second and available CPU/GPU/NPU metrics.
3. **Behavior-first comparison** — a faster model cannot outrank a more behaviorally reliable model solely on throughput.
4. **Auditability** — the three public rules and cases are readable in `src/nviq_lemonade/evaluation.py` and `cases/v0.1/public.json`.
5. **Portable report** — `comparison.html` opens directly from disk and contains no hosted dependencies.

## Explicit two-model run

```bash
nviq-lemonade compare \
  --model MODEL_A \
  --model MODEL_B \
  --output-dir out/reviewer-compare
```

Artifacts:

```text
out/reviewer-compare/
  comparison.json
  comparison.md
  comparison.html
  models/<model>/report.{json,md,html}
```

## Reproduce software verification

```bash
python scripts/verify.py
```

The automated suite uses a Lemonade-compatible in-process fixture and therefore does not require accelerator hardware.

## Result integrity

Fixture outputs prove code behavior only. Any published real hardware result must follow `results/README.md` and retain the original JSON output from a live Lemonade run.
