from nviq_lemonade.html_reporting import comparison_html, single_report_html


REPORT = {
    "suite": "NVIQ × Lemonade Open Evaluation v0.2",
    "model": {"id": "Model-<script>alert(1)</script>", "recipe": "llamacpp"},
    "lemonade": {"health": {"status": "ok", "version": "9.0"}, "system_info": {"Processor": "AMD Fixture"}},
    "summary": {"cases": 1, "passed": 1, "failed": 0, "pass_rate": 1.0, "total_wall_time_ms": 10.0},
    "performance": {"mean_tokens_per_second": 42.0, "mean_time_to_first_token_s": 0.2, "mean_wall_time_ms": 10.0, "peak_gpu_percent": 55.0, "peak_vram_gb": 2.0, "peak_npu_percent": None},
    "results": [{"case_id": "case-1", "family": "Context Integrity", "response": "safe", "wall_time_ms": 10.0, "evaluation": {"pass": True, "evidence": "all facts preserved"}}],
}


def test_single_report_html_is_self_contained_and_escapes_untrusted_text():
    page = single_report_html(REPORT)
    assert "<!doctype html>" in page.lower()
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page
    assert "<script>alert(1)</script>" not in page
    assert "Context Integrity" in page
    assert "42.0" in page
    assert "https://" not in page


def test_comparison_html_shows_behavior_and_runtime_dimensions():
    comparison = {
        "suite": "NVIQ × Lemonade Model Comparison v0.2",
        "ranking": ["Model-A", "Model-B"],
        "best_behavioral_model": "Model-A",
        "models": [
            {"model_id": "Model-A", "recipe": "llamacpp", "pass_rate": 1.0, "passed": 3, "cases": 3, "mean_tokens_per_second": 20.0, "mean_time_to_first_token_s": 0.2, "mean_wall_time_ms": 100.0, "peak_gpu_percent": 50.0, "peak_vram_gb": 2.0, "peak_npu_percent": None},
            {"model_id": "Model-B", "recipe": "ryzenai-llm", "pass_rate": 0.6667, "passed": 2, "cases": 3, "mean_tokens_per_second": 60.0, "mean_time_to_first_token_s": 0.1, "mean_wall_time_ms": 80.0, "peak_gpu_percent": None, "peak_vram_gb": None, "peak_npu_percent": 30.0},
        ],
    }
    page = comparison_html(comparison)
    assert "Model-A" in page
    assert "Model-B" in page
    assert "100.0%" in page
    assert "66.7%" in page
    assert "60.0" in page
    assert "Behavior first" in page
