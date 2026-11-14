"""Download selected GitHub pull request files into an isolated workspace."""

import os
import re
import shutil
import ssl
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import certifi


MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024


class CandidateDownloadError(Exception):
    """Raised when a candidate file cannot be downloaded."""


def _validate_repository(repository: str) -> None:
    if not isinstance(repository, str) or not re.fullmatch(
        r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",
        repository,
    ):
        raise ValueError("Repository must use the owner/repository format.")


def _validate_commit_sha(commit_sha: str) -> None:
    if not isinstance(commit_sha, str) or not re.fullmatch(
        r"[0-9a-fA-F]{40}",
        commit_sha,
    ):
        raise ValueError("Commit SHA must be a valid 40-character SHA-1.")


def _validate_file_path(file_path: str) -> PurePosixPath:
    if not isinstance(file_path, str) or not file_path:
        raise ValueError("Candidate file path cannot be empty.")

    if "\\" in file_path:
        raise ValueError("Backslashes are not allowed in candidate paths.")

    path = PurePosixPath(file_path)

    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise ValueError("Candidate file path must stay inside the workspace.")

    return path


def download_candidate_files(
    repository: str,
    commit_sha: str,
    selected_files: list[str],
    destination: Path,
    token: str | None = None,
    timeout: int = 15,
) -> list[Path]:
    """Download selected files from an exact GitHub commit.

    The destination must not already exist. Downloaded files are stored
    without executing them or modifying the source repository.
    """

    _validate_repository(repository)
    _validate_commit_sha(commit_sha)

    if not isinstance(selected_files, list) or not selected_files:
        raise ValueError("Select at least one candidate file.")

    if isinstance(timeout, bool) or not isinstance(timeout, int) or timeout <= 0:
        raise ValueError("Timeout must be a positive integer.")

    validated_paths = [_validate_file_path(file_path) for file_path in selected_files]

    if len(set(validated_paths)) != len(validated_paths):
        raise ValueError("Duplicate candidate file paths are not allowed.")

    original_destination = Path(destination)

    if original_destination.is_symlink() or original_destination.exists():
        raise FileExistsError("Candidate destination already exists or is a symlink.")

    destination = original_destination.resolve()

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.mkdir()

    auth_token = token or os.getenv("GITHUB_TOKEN")
    downloaded_files = []

    ssl_context = ssl.create_default_context(cafile=certifi.where())
    try:
        for relative_path in validated_paths:
            encoded_path = quote(relative_path.as_posix(), safe="/")
            url = (
                f"https://raw.githubusercontent.com/"
                f"{repository}/{commit_sha}/{encoded_path}"
            )

            headers = {
                "User-Agent": "FiberLab-Guardian",
                "Accept": "application/vnd.github.raw+json",
            }

            if auth_token:
                headers["Authorization"] = f"Bearer {auth_token}"

            request = Request(url, headers=headers, method="GET")

            try:
                with urlopen(
                    request,
                    timeout=timeout,
                    context=ssl_context,
                ) as response:
                    content = response.read(MAX_FILE_SIZE_BYTES + 1)
                    if len(content) > MAX_FILE_SIZE_BYTES:
                        raise CandidateDownloadError(
                            f"Candidate file {relative_path} exceeds the "
                            f"{MAX_FILE_SIZE_BYTES}-byte download limit."
                        )

            except HTTPError as error:
                raise CandidateDownloadError(
                    f"GitHub returned HTTP {error.code} "
                    f"while downloading {relative_path}."
                ) from error

            except (URLError, TimeoutError, OSError) as error:
                raise CandidateDownloadError(
                    f"Unable to download {relative_path} from GitHub."
                ) from error

            target = destination.joinpath(*relative_path.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)

            downloaded_files.append(target)

    except Exception:
        # Remove an incomplete candidate workspace.

        shutil.rmtree(destination, ignore_errors=True)
        raise

    return downloaded_files
