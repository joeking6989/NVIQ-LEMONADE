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
    assert report["lemonade"]["health"]["status"] == "ok"
