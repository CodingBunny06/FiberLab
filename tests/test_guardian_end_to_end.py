"""End-to-end tests for the FiberLab Guardian pipeline."""

from guardian.runner import run_guardian
from guardian.test_runner import CommandResult


def test_guardian_completes_full_workflow(tmp_path, monkeypatch):
    """Verify workspace creation, integration, inspection and quality checks."""

    project = tmp_path / "project"
    candidate = tmp_path / "candidate"
    workspace = tmp_path / "workspace"

    project.mkdir()
    candidate.mkdir()

    (project / "app.py").write_text("print('original')\n")
    (candidate / "app.py").write_text("print('candidate')\n")

    calls = []

    def mock_run_command(command, workspace_root, timeout_seconds):
        calls.append(command)
        return CommandResult("PASS", 0, "Success", "")

    monkeypatch.setattr("guardian.runner.run_command", mock_run_command)

    report = run_guardian(
        project,
        candidate,
        ["app.py"],
        workspace,
    )

    assert workspace.exists()
    assert (workspace / "app.py").read_text() == "print('candidate')\n"
    assert (project / "app.py").read_text() == "print('original')\n"

    assert len(calls) == 2
    assert report.failed == 0
    assert report.passed >= 2


def test_guardian_stops_after_structural_failure(tmp_path, monkeypatch):
    """Verify invalid candidate syntax prevents quality-check execution."""

    project = tmp_path / "project"
    candidate = tmp_path / "candidate"
    workspace = tmp_path / "workspace"

    project.mkdir()
    candidate.mkdir()

    (project / "app.py").write_text("print('original')\n")

    physics_dir = candidate / "physics"
    physics_dir.mkdir()

    (physics_dir / "numerical_aperture.py").write_text("def broken_function(\n")

    def unexpected_command(*args, **kwargs):
        raise AssertionError("Quality checks should not execute.")

    monkeypatch.setattr(
        "guardian.runner.run_command",
        unexpected_command,
    )

    report = run_guardian(
        project,
        candidate,
        ["physics/numerical_aperture.py"],
        workspace,
    )

    assert report.failed >= 1
    assert report.overall_status == "FAIL"


def test_guardian_reports_quality_check_failure(tmp_path, monkeypatch):
    """Verify failed automated checks appear in the final report."""

    project = tmp_path / "project"
    candidate = tmp_path / "candidate"
    workspace = tmp_path / "workspace"

    project.mkdir()
    candidate.mkdir()

    (project / "app.py").write_text("print('original')\n")
    (candidate / "app.py").write_text("print('candidate')\n")

    calls = []

    def mock_run_command(command, workspace_root, timeout_seconds):
        calls.append(command)

        if command[0] == "ruff":
            return CommandResult("FAIL", 1, "", "Ruff detected an issue.")

        return CommandResult("PASS", 0, "Tests passed", "")

    monkeypatch.setattr("guardian.runner.run_command", mock_run_command)

    report = run_guardian(
        project,
        candidate,
        ["app.py"],
        workspace,
    )

    assert len(calls) == 2
    assert report.failed == 1
    assert report.overall_status == "FAIL"
    assert any(
        "Ruff detected an issue." in item.recommendation for item in report.diagnostics
    )
