
"""Tests for the FiberLab Guardian integration engine."""


import pytest

from guardian.integration_engine import (
    create_integration_workspace,
    integrate_candidate_modules,
)


def test_workspace_copies_project_files(tmp_path):
    source = tmp_path / "source"
    destination = tmp_path / "workspace"

    source.mkdir()
    (source / "app.py").write_text("print('FiberLab')", encoding="utf-8")

    result = create_integration_workspace(source, destination)

    assert result == destination
    assert (destination / "app.py").read_text(encoding="utf-8") == (
        "print('FiberLab')"
    )


def test_workspace_excludes_development_directories(tmp_path):
    source = tmp_path / "source"
    destination = tmp_path / "workspace"

    source.mkdir()
    (source / "app.py").write_text("print('FiberLab')", encoding="utf-8")

    for directory in (".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache"):
        ignored = source / directory
        ignored.mkdir()
        (ignored / "internal.txt").write_text("exclude me", encoding="utf-8")

    create_integration_workspace(source, destination)

    for directory in (".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache"):
        assert not (destination / directory).exists()


def test_workspace_refuses_existing_destination(tmp_path):
    source = tmp_path / "source"
    destination = tmp_path / "workspace"

    source.mkdir()
    destination.mkdir()

    with pytest.raises(FileExistsError):
        create_integration_workspace(source, destination)


def test_workspace_rejects_missing_source(tmp_path):
    source = tmp_path / "missing"
    destination = tmp_path / "workspace"

    with pytest.raises(FileNotFoundError):
        create_integration_workspace(source, destination)


def test_integrates_selected_candidate_module(tmp_path):
    candidate = tmp_path / "candidate"
    workspace = tmp_path / "workspace"

    (candidate / "physics").mkdir(parents=True)
    (workspace / "physics").mkdir(parents=True)

    source_file = candidate / "physics" / "attenuation.py"
    source_file.write_text("def calculate_loss():\n    return 5\n", encoding="utf-8")

    result = integrate_candidate_modules(
        candidate,
        workspace,
        ["physics/attenuation.py"],
    )

    destination_file = workspace / "physics" / "attenuation.py"

    assert destination_file.exists()
    assert destination_file.read_text(encoding="utf-8") == source_file.read_text(
        encoding="utf-8"
    )
    assert result == [destination_file]


def test_integrates_only_selected_files(tmp_path):
    candidate = tmp_path / "candidate"
    workspace = tmp_path / "workspace"

    candidate.mkdir()
    workspace.mkdir()

    (candidate / "selected.py").write_text("selected = True", encoding="utf-8")
    (candidate / "unselected.py").write_text("unselected = True", encoding="utf-8")

    integrate_candidate_modules(candidate, workspace, ["selected.py"])

    assert (workspace / "selected.py").exists()
    assert not (workspace / "unselected.py").exists()


def test_integrates_candidate_into_existing_workspace_file(tmp_path):
    candidate = tmp_path / "candidate"
    workspace = tmp_path / "workspace"

    candidate.mkdir()
    workspace.mkdir()

    (candidate / "app.py").write_text("candidate version", encoding="utf-8")
    (workspace / "app.py").write_text("placeholder version", encoding="utf-8")

    integrate_candidate_modules(candidate, workspace, ["app.py"])

    assert (workspace / "app.py").read_text(encoding="utf-8") == "candidate version"


def test_rejects_missing_candidate_file(tmp_path):
    candidate = tmp_path / "candidate"
    workspace = tmp_path / "workspace"

    candidate.mkdir()
    workspace.mkdir()

    with pytest.raises(FileNotFoundError):
        integrate_candidate_modules(candidate, workspace, ["physics/missing.py"])


def test_rejects_unsafe_candidate_path(tmp_path):
    candidate = tmp_path / "candidate"
    workspace = tmp_path / "workspace"

    candidate.mkdir()
    workspace.mkdir()

    with pytest.raises(ValueError):
        integrate_candidate_modules(candidate, workspace, ["../outside.py"])
