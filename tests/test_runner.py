from nviq_lemonade.runner import run_suite


CASES = [
    {
        "case_id": "context-integrity-001",
        "family": "Context Integrity",
        "messages": [{"role": "user", "content": "context"}],
        "rule": "contains_required_facts",
        "expected": {"required_facts": ["Tuesday", "Thursday", "ORBIT-7"]},
    },
    {
        "case_id": "prior-contamination-001",
        "family": "Prior-Contamination Resistance",
        "messages": [{"role": "user", "content": "prior"}],
        "rule": "rejects_false_prior",
        "expected": {"current_answer": "blue", "false_prior": "red"},
    },
    {
        "case_id": "confidence-discipline-001",
        "family": "Confidence Discipline",
        "messages": [{"role": "user", "content": "confidence"}],
        "rule": "confidence_matches_evidence",
        "expected": {"uncertainty_markers": ["uncertain"]},
    },
]


class FakeClient:
    def __init__(self):
        self.responses = iter([
            "Tuesday is primary, Thursday is backup, mission ORBIT-7.",
            "The current indicator is blue.",
            "The exact value is uncertain because the sensors disagree.",
        ])

    def health(self):
        return {"status": "ok", "version": "fixture-1.0"}

    def system_info(self):
        return {"os": "fixture-os"}

    def models(self):
        return [{"id": "Fixture-Model", "recipe": "fixture", "downloaded": True}]

    def chat(self, model, messages, temperature=0.0):
        return {"choices": [{"message": {"content": next(self.responses)}}]}

    def stats(self):
        return {"tokens_per_second": 42.0}

    def system_stats(self):
        return {"cpu_percent": 10.0, "gpu_percent": 20.0, "vram_gb": 1.0, "npu_percent": None}


def test_run_suite_combines_model_behavior_and_lemonade_telemetry():
    report = run_suite(FakeClient(), "Fixture-Model", CASES)
    assert report["model"]["id"] == "Fixture-Model"
    assert report["summary"]["cases"] == 3
    assert report["summary"]["passed"] == 3
    assert report["summary"]["failed"] == 0
    assert report["summary"]["pass_rate"] == 1.0
    assert len(report["results"]) == 3
    assert all("wall_time_ms" in row for row in report["results"])
    assert all(row["lemonade_stats"]["tokens_per_second"] == 42.0 for row in report["results"])
    assert all("system_stats" in row for row in report["results"])
    assert report["lemonade"]["health"]["status"] == "ok"


class TelemetryClient(FakeClient):
    def __init__(self):
        super().__init__()
        self._stats = iter([
            {"time_to_first_token": 0.1, "tokens_per_second": 20.0, "input_tokens": 10, "output_tokens": 4},
            {"time_to_first_token": 0.2, "tokens_per_second": 30.0, "input_tokens": 20, "output_tokens": 5},
            {"time_to_first_token": 0.3, "tokens_per_second": 40.0, "input_tokens": 30, "output_tokens": 6},
        ])
        self._system_stats = iter([
            {"cpu_percent": 10.0, "gpu_percent": 30.0, "vram_gb": 1.5, "npu_percent": None},
            {"cpu_percent": 25.0, "gpu_percent": 50.0, "vram_gb": 2.0, "npu_percent": 12.0},
            {"cpu_percent": 15.0, "gpu_percent": None, "vram_gb": 1.75, "npu_percent": 8.0},
        ])

    def stats(self):
        return next(self._stats)

    def system_stats(self):
        return next(self._system_stats)


def test_run_suite_aggregates_available_runtime_telemetry():
    report = run_suite(TelemetryClient(), "Fixture-Model", CASES)
    perf = report["performance"]
    assert perf["mean_time_to_first_token_s"] == 0.2
    assert perf["mean_tokens_per_second"] == 30.0
    assert perf["input_tokens_total"] == 60
    assert perf["output_tokens_total"] == 15
    assert perf["peak_cpu_percent"] == 25.0
    assert perf["peak_gpu_percent"] == 50.0
    assert perf["peak_vram_gb"] == 2.0
    assert perf["peak_npu_percent"] == 12.0
    assert len(report["results"]) == 3
