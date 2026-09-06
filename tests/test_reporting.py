import json

from nviq_lemonade.reporting import write_report


REPORT = {
    "schema_version": "0.1",
    "suite": "NVIQ × Lemonade Open Evaluation v0.1",
    "lemonade": {"health": {"status": "ok", "version": "fixture-1.0"}, "system_info": {"os": "fixture-os"}},
    "model": {"id": "Fixture-Model", "recipe": "fixture"},
    "summary": {"cases": 2, "passed": 1, "failed": 1, "pass_rate": 0.5, "total_wall_time_ms": 12.3},
    "results": [
        {
            "case_id": "case-a",
            "family": "Context Integrity",
            "response": "response a",
            "wall_time_ms": 5.1,
            "lemonade_stats": {"tokens_per_second": 42.0},
            "evaluation": {"case_id": "case-a", "rule": "contains_required_facts", "pass": True, "score": 1.0, "evidence": "ok"},
        },
        {
            "case_id": "case-b",
            "family": "Confidence Discipline",
            "response": "response b",
            "wall_time_ms": 7.2,
            "lemonade_stats": None,
            "evaluation": {"case_id": "case-b", "rule": "confidence_matches_evidence", "pass": False, "score": 0.0, "evidence": "missing uncertainty"},
        },
    ],
}


def test_write_report_creates_json_and_markdown(tmp_path):
    json_path, md_path = write_report(REPORT, tmp_path)
    assert json.loads(json_path.read_text(encoding="utf-8")) == REPORT
    markdown = md_path.read_text(encoding="utf-8")
    assert "Fixture-Model" in markdown
    assert "50.0%" in markdown
    assert "case-a" in markdown
    assert "case-b" in markdown
    assert "PASS" in markdown
    assert "FAIL" in markdown
