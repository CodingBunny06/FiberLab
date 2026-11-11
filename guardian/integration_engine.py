
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

def integrate_candidate_modules(
    candidate_root: Path,
    workspace_root: Path,
    selected_files: list[str],
) -> list[Path]:
    """Copy selected candidate modules into an isolated integration workspace."""
    candidate_root = candidate_root.resolve()
    workspace_root = workspace_root.resolve()

    if not candidate_root.is_dir():
        raise FileNotFoundError(
            f"Candidate directory does not exist: {candidate_root}"
        )

    if not workspace_root.is_dir():
        raise FileNotFoundError(
            f"Integration workspace does not exist: {workspace_root}"
        )

    integrated_files = []

    for relative_path in selected_files:
        relative_path = Path(relative_path)

        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise ValueError(f"Unsafe candidate path: {relative_path}")

        source_file = (candidate_root / relative_path).resolve()

        if not source_file.is_relative_to(candidate_root):
            raise ValueError(f"Unsafe candidate path: {relative_path}")

        if not source_file.is_file():
            raise FileNotFoundError(
                f"Candidate file does not exist: {source_file}"
            )

        if source_file.is_symlink():
            raise ValueError(f"Symlinks are not allowed: {relative_path}")

        destination_file = workspace_root / relative_path
        destination_file.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(source_file, destination_file)
        integrated_files.append(destination_file)

    return integrated_files
