from http_fixture import fixture_server
from nviq_lemonade.cli import main


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
    assert "report.json" in capsys.readouterr().out
