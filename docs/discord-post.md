# #AMDDevChallenge post copy

Built **NVIQ × Lemonade** 🍋 — an open-source local-AI evaluation tool that combines **behavioral reliability** with Lemonade runtime telemetry.

Instead of ranking local models on speed alone, it runs transparent probes for:
- Context Integrity
- Prior-Contamination Resistance
- Confidence Discipline

Then it captures Lemonade TTFT / tokens-per-second plus available CPU, GPU, VRAM and NPU telemetry and generates a self-contained JSON + Markdown + HTML comparison bundle.

The comparison is deliberately **behavior first, speed second**: a faster model does not outrank a more reliable model solely on throughput.

One-command reviewer flow:

```bash
nviq-lemonade demo --output-dir out/demo
```

Repo: https://github.com/joeking6989/NVIQ-LEMONADE

Apache-2.0. Feedback and model/hardware comparison runs are welcome. #AMDDevChallenge #Lemonade #LocalAI
