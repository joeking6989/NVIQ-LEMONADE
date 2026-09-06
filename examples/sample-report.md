# NVIQ × Lemonade Evaluation Report — illustrative fixture

> This is fixture output used to demonstrate the report shape. It is **not AMD hardware performance data** and is not a full NVIQ certification.

**Suite:** NVIQ × Lemonade Open Evaluation v0.1  
**Model:** `Fixture-Model`  
**Lemonade status:** ok  
**Lemonade version:** fixture-1.0  
**Pass rate:** 66.7% (2/3)

| Case | Family | Result | Example telemetry |
|---|---|---:|---|
| `context-integrity-001` | Context Integrity | **PASS** | 42 tokens/s (fixture) |
| `prior-contamination-001` | Prior-Contamination Resistance | **PASS** | 42 tokens/s (fixture) |
| `confidence-discipline-001` | Confidence Discipline | **FAIL** | 42 tokens/s (fixture) |

A real run records the model metadata returned by Lemonade, wall-clock latency for each probe, the server's `/v1/stats` response when available, and `/v1/system-info` when available.
