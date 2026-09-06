import json

import pytest

from http_fixture import fixture_server
from nviq_lemonade.cli import _select_demo_models, main


def test_doctor_prints_server_and_model_inventory(capsys):
    with fixture_server() as (base_url, _handler):
        code = main(["--base-url", base_url, "doctor"])
    assert code == 0
    output = capsys.readouterr().out
    assert "fixture-1.0" in output
    assert "Fixture-Model" in output


def test_run_writes_reports(tmp_path, capsys):
    with fixture_server() as (base_url, _handler):
        code = main([
            "--base-url",
            base_url,
            "run",
            "--model",
            "Fixture-Model",
            "--output-dir",
            str(tmp_path),
        ])
    assert code == 0
    assert (tmp_path / "report.json").exists()
    assert (tmp_path / "report.md").exists()
    assert (tmp_path / "report.html").exists()
    assert "report.json" in capsys.readouterr().out


def test_compare_writes_complete_reviewer_bundle(tmp_path, capsys):
    with fixture_server() as (base_url, _handler):
        code = main([
            "--base-url", base_url,
            "compare",
            "--model", "Fixture-Model",
            "--model", "Fixture-Model-B",
            "--output-dir", str(tmp_path),
        ])
    assert code == 0
    assert (tmp_path / "comparison.json").exists()
    assert (tmp_path / "comparison.md").exists()
    assert (tmp_path / "comparison.html").exists()
    comparison = json.loads((tmp_path / "comparison.json").read_text(encoding="utf-8"))
    assert comparison["ranking"] == ["Fixture-Model", "Fixture-Model-B"]
    model_dirs = list((tmp_path / "models").iterdir())
    assert len(model_dirs) == 2
    assert all((directory / "report.html").exists() for directory in model_dirs)
    assert "comparison.html" in capsys.readouterr().out


def test_demo_discovers_downloaded_local_models_and_honors_limit(tmp_path):
    with fixture_server() as (base_url, _handler):
        code = main(["--base-url", base_url, "demo", "--max-models", "1", "--output-dir", str(tmp_path)])
    assert code == 0
    comparison = json.loads((tmp_path / "comparison.json").read_text(encoding="utf-8"))
    assert [row["model_id"] for row in comparison["models"]] == ["Fixture-Model"]


def test_select_demo_models_filters_cloud_and_rejects_empty_inventory():
    inventory = [
        {"id": "Local-A", "recipe": "llamacpp", "downloaded": True},
        {"id": "cloud.model", "recipe": "cloud", "downloaded": True},
        {"id": "Not-Downloaded", "recipe": "llamacpp", "downloaded": False},
        {"id": "Local-B", "recipe": "ryzenai-llm", "downloaded": True},
    ]
    assert _select_demo_models(inventory, explicit=None, max_models=1) == ["Local-A"]
    assert _select_demo_models(inventory, explicit=["Local-B"], max_models=1) == ["Local-B"]
    with pytest.raises(ValueError, match="No downloaded local models"):
        _select_demo_models([], explicit=None, max_models=2)
