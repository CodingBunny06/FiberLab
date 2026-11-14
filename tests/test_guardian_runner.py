"""Tests for the FiberLab Guardian execution pipeline."""

from guardian.runner import run_guardian


def test_guardian_creates_workspace_and_generates_report(tmp_path):
    project = tmp_path / "project"
    candidate = tmp_path / "candidate"
    workspace = tmp_path / "workspace"

    project.mkdir()
    candidate.mkdir()

    (project / "app.py").write_text("print('FiberLab')", encoding="utf-8")
    (candidate / "app.py").write_text(
        "print('Candidate FiberLab')",
        encoding="utf-8",
    )

    report = run_guardian(
        project_root=project,
        candidate_root=candidate,
        selected_files=["app.py"],
        workspace_root=workspace,
        run_quality_checks=False,
    )

    assert workspace.exists()
    assert (workspace / "app.py").read_text(encoding="utf-8") == (
        "print('Candidate FiberLab')"
    )
    assert report is not None
    assert report.overall_status in ("PASS", "PENDING", "FAIL")


def test_guardian_does_not_modify_original_project(tmp_path):
    project = tmp_path / "project"
    candidate = tmp_path / "candidate"
    workspace = tmp_path / "workspace"

    project.mkdir()
    candidate.mkdir()

    original_content = "print('Original FiberLab')"
    (project / "app.py").write_text(original_content, encoding="utf-8")
    (candidate / "app.py").write_text(
        "print('Candidate version')",
        encoding="utf-8",
    )

    run_guardian(
        project_root=project,
        candidate_root=candidate,
        selected_files=["app.py"],
        workspace_root=workspace,
        run_quality_checks=False,
    )

    assert (project / "app.py").read_text(encoding="utf-8") == original_content


def test_guardian_rejects_missing_candidate_file(tmp_path):
    project = tmp_path / "project"
    candidate = tmp_path / "candidate"
    workspace = tmp_path / "workspace"

    project.mkdir()
    candidate.mkdir()

    (project / "app.py").write_text("print('FiberLab')", encoding="utf-8")

    try:
        run_guardian(
            project_root=project,
            candidate_root=candidate,
            selected_files=["physics/missing.py"],
            workspace_root=workspace,
            run_quality_checks=False,
        )
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("Expected FileNotFoundError")


def test_guardian_rejects_existing_workspace(tmp_path):
    project = tmp_path / "project"
    candidate = tmp_path / "candidate"
    workspace = tmp_path / "workspace"

    project.mkdir()
    candidate.mkdir()
    workspace.mkdir()

    try:
        run_guardian(
            project_root=project,
            candidate_root=candidate,
            selected_files=[],
            workspace_root=workspace,
            run_quality_checks=False,
        )
    except FileExistsError:
        pass
    else:
        raise AssertionError("Expected FileExistsError")
