"""Build isolated workspaces for FiberLab Guardian integration checks."""

import os
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
    source_root = Path(source_root).resolve()
    original_destination = Path(destination)

    # Reject existing destinations and symlinks before resolving.
    if original_destination.is_symlink() or original_destination.exists():
        raise FileExistsError(
            f"Integration workspace already exists: {original_destination}"
        )

    destination = original_destination.resolve()

    if not source_root.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source_root}")

    if not source_root.is_dir():
        raise NotADirectoryError(f"Source path is not a directory: {source_root}")

    if destination.is_relative_to(source_root):
        raise ValueError("Integration workspace must be outside the source project.")

    # Check only files and directories that will actually be copied.
    for current_root, directory_names, file_names in os.walk(
        source_root,
        topdown=True,
        followlinks=False,
    ):
        current_path = Path(current_root)

        # Exclude development directories before inspecting their contents.
        directory_names[:] = [
            name for name in directory_names if name not in IGNORED_DIRECTORIES
        ]

        # Reject symlink directories that would otherwise be copied.
        for name in directory_names:
            path = current_path / name

            if path.is_symlink():
                raise ValueError(
                    f"Symlinks are not allowed in the source project: {path}"
                )

        # Reject symlink files that would otherwise be copied.
        for name in file_names:
            if name in IGNORED_FILES or name.endswith(".pyc"):
                continue

            path = current_path / name

            if path.is_symlink():
                raise ValueError(
                    f"Symlinks are not allowed in the source project: {path}"
                )

    def ignore_development_files(
        directory: str,
        names: list[str],
    ) -> set[str]:
        """Exclude environments, caches, and coverage files."""
        return {
            name
            for name in names
            if name in IGNORED_DIRECTORIES
            or name in IGNORED_FILES
            or name.endswith(".pyc")
        }

    shutil.copytree(
        source_root,
        destination,
        ignore=ignore_development_files,
    )

    return destination


def integrate_candidate_modules(
    candidate_root: Path,
    workspace_root: Path,
    selected_files: list[str],
) -> list[Path]:
    """Copy selected candidate modules into an isolated integration workspace."""
    candidate_root = Path(candidate_root).resolve()
    workspace_root = Path(workspace_root).resolve()

    if not candidate_root.is_dir():
        raise FileNotFoundError(f"Candidate directory does not exist: {candidate_root}")

    if not workspace_root.is_dir():
        raise FileNotFoundError(
            f"Integration workspace does not exist: {workspace_root}"
        )

    integrated_files = []

    for relative_path in selected_files:
        relative_path = Path(relative_path)

        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise ValueError(f"Unsafe candidate path: {relative_path}")

        # Check original path components before resolving symlinks.
        candidate_path = candidate_root / relative_path
        current_path = candidate_root

        for part in relative_path.parts:
            current_path = current_path / part

            if current_path.is_symlink():
                raise ValueError(f"Symlinks are not allowed: {relative_path}")

        source_file = candidate_path.resolve()

        if not source_file.is_relative_to(candidate_root):
            raise ValueError(f"Unsafe candidate path: {relative_path}")

        if not source_file.is_file():
            raise FileNotFoundError(f"Candidate file does not exist: {source_file}")

        destination_file = workspace_root / relative_path
        destination_file.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(source_file, destination_file)
        integrated_files.append(destination_file)

    return integrated_files
