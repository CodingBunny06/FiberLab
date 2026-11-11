
"""Tests for the FiberLab Guardian integration engine."""


import pytest

from guardian.integration_engine import create_integration_workspace


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

