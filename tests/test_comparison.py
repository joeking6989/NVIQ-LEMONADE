import pytest

from nviq_lemonade.comparison import compare_models
from test_runner import CASES


class ComparisonClient:
    def __init__(self):
        self.last_model = None

    def health(self):
        return {"status": "ok", "version": "fixture-1.0"}

    def system_info(self):
        return {"os": "fixture-os"}

    def models(self):
        return [
            {"id": "Model-A", "recipe": "llamacpp", "downloaded": True},
            {"id": "Model-B", "recipe": "ryzenai-llm", "downloaded": True},
        ]

    def chat(self, model, messages, temperature=0.0):
        self.last_model = model
        prompt = messages[-1]["content"]
        if "context" in prompt:
            text = "Tuesday, Thursday, ORBIT-7"
        elif "prior" in prompt:
            text = "The current indicator is blue."
        elif model == "Model-A":
            text = "The exact value is uncertain."
        else:
            text = "The exact true value is 42."
        return {"choices": [{"message": {"content": text}}]}

    def stats(self):
        tps = 20.0 if self.last_model == "Model-A" else 60.0
        return {
            "time_to_first_token": 0.2,
            "tokens_per_second": tps,
            "input_tokens": 10,
            "output_tokens": 5,
        }

    def system_stats(self):
        return {"cpu_percent": 20.0, "gpu_percent": 40.0, "vram_gb": 2.0, "npu_percent": None}


def test_compare_models_prioritizes_behavior_before_raw_speed():
    comparison = compare_models(ComparisonClient(), ["Model-B", "Model-A"], CASES)
    assert comparison["schema_version"] == "0.2"
    assert comparison["ranking"] == ["Model-A", "Model-B"]
    assert comparison["best_behavioral_model"] == "Model-A"
    rows = {row["model_id"]: row for row in comparison["models"]}
    assert rows["Model-A"]["pass_rate"] == 1.0
    assert rows["Model-A"]["mean_tokens_per_second"] == 20.0
    assert rows["Model-B"]["pass_rate"] == pytest.approx(2 / 3, abs=0.0001)
    assert rows["Model-B"]["mean_tokens_per_second"] == 60.0
    assert len(comparison["reports"]) == 2


def test_compare_models_rejects_duplicate_or_empty_model_lists():
    client = ComparisonClient()
    with pytest.raises(ValueError, match="at least one"):
        compare_models(client, [], CASES)
    with pytest.raises(ValueError, match="duplicate"):
        compare_models(client, ["Model-A", "Model-A"], CASES)
