
"""Tests for the FiberLab Guardian automated test runner."""

import subprocess

from guardian.test_runner import run_command


def test_successful_command_returns_pass(monkeypatch, tmp_path):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args[0], 0, stdout="All checks passed", stderr=""
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_command(["ruff", "check", "."], tmp_path)

    assert result.status == "PASS"
    assert result.return_code == 0
    assert result.stdout == "All checks passed"
    assert result.stderr == ""


def test_failed_command_returns_fail(monkeypatch, tmp_path):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args[0], 1, stdout="", stderr="Lint errors found"
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_command(["ruff", "check", "."], tmp_path)

    assert result.status == "FAIL"
    assert result.return_code == 1
    assert result.stderr == "Lint errors found"


def test_timed_out_command_returns_timeout(monkeypatch, tmp_path):
    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_command(
        ["python", "-m", "pytest"],
        tmp_path,
        timeout_seconds=5,
    )

    assert result.status == "TIMEOUT"
    assert result.return_code is None


def test_execution_error_is_captured(monkeypatch, tmp_path):
    def fake_run(*args, **kwargs):
        raise OSError("Command could not start")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_command(["missing-command"], tmp_path)

    assert result.status == "ERROR"
    assert result.return_code is None
    assert "could not start" in result.stderr.lower()


def test_command_runs_in_requested_workspace(monkeypatch, tmp_path):
    captured = {}

    def fake_run(*args, **kwargs):
        captured["cwd"] = kwargs["cwd"]
        return subprocess.CompletedProcess(
            args[0], 0, stdout="", stderr=""
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    run_command(["ruff", "check", "."], tmp_path)

    assert captured["cwd"] == tmp_path
