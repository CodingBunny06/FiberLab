
"""Build isolated workspaces for FiberLab Guardian integration checks."""

import shutil
from pathlib import Path

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "htmlcov",
}

IGNORED_FILES = {
    ".coverage",
}


def create_integration_workspace(
    source_root: Path,
    destination: Path,
) -> Path:
    """Copy a project into an isolated workspace, excluding development files."""
    source_root = source_root.resolve()
    destination = destination.resolve()

    if not source_root.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source_root}")

    if not source_root.is_dir():
        raise NotADirectoryError(f"Source path is not a directory: {source_root}")

    if destination.exists():
        raise FileExistsError(
            f"Integration workspace already exists: {destination}"
        )

    if destination.is_relative_to(source_root):
        raise ValueError(
            "Integration workspace must be outside the source project."
        )

    for path in source_root.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Symlinks are not allowed in the source project: {path}")

    def ignore_development_files(
        directory: str,
        names: list[str],
    ) -> set[str]:
        """Exclude environments, caches, and coverage files."""
        return {
            name
            for name in names
            if name in IGNORED_DIRECTORIES or name in IGNORED_FILES
            or name.endswith(".pyc")
        }

    shutil.copytree(
        source_root,
        destination,
        ignore=ignore_development_files,
    )

    return destination
