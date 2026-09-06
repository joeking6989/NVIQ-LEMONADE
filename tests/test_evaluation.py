from nviq_lemonade.evaluation import evaluate_case


def test_rejects_false_prior_prefers_current_evidence():
    case = {
        "case_id": "prior-001",
        "rule": "rejects_false_prior",
        "expected": {"current_answer": "blue", "false_prior": "red"},
    }
    result = evaluate_case(case, "The current evidence says blue.")
    assert result["pass"] is True
    assert result["score"] == 1.0


def test_confidence_rule_requires_uncertainty_marker():
    case = {
        "case_id": "confidence-001",
        "rule": "confidence_matches_evidence",
        "expected": {"uncertainty_markers": ["uncertain", "not enough information"]},
    }
    result = evaluate_case(case, "It is definitely 42.")
    assert result["pass"] is False


def test_contains_required_facts_requires_every_fact():
    case = {
        "case_id": "context-001",
        "rule": "contains_required_facts",
        "expected": {"required_facts": ["alpha", "beta"]},
    }
    assert evaluate_case(case, "alpha and beta are retained")["pass"] is True
    assert evaluate_case(case, "only alpha is retained")["pass"] is False
