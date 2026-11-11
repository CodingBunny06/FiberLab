
"""Connect GitHub pull requests to the FiberLab Guardian pipeline."""

from dataclasses import dataclass
from pathlib import Path

from guardian.candidate_downloader import download_candidate_files
from guardian.github_client import ChangedFile, GitHubClient, PullRequestInfo
from guardian.reporter import GuardianReport
from guardian.runner import run_guardian


@dataclass
class PullRequestInspectionResult:
    """Store the results of inspecting a GitHub pull request."""

    pull_request: PullRequestInfo
    changed_files: list[ChangedFile]
    downloaded_files: list[Path]
    report: GuardianReport


def inspect_pull_request(
    repository: str,
    pr_number: int,
    project_root: Path,
    candidate_workspace: Path,
    integration_workspace: Path,
    token: str | None = None,
) -> PullRequestInspectionResult:
    """Download and statically inspect the files changed by a GitHub PR."""

    client = GitHubClient(token=token)

    pull_request = client.get_pull_request(repository, pr_number)
    changed_files = client.list_changed_files(repository, pr_number)

    # Deleted files have no current file content to download.
    downloadable_files = [
        changed_file
        for changed_file in changed_files
        if changed_file.status != "removed"
    ]

    if not downloadable_files:
        raise ValueError("The pull request contains no downloadable files.")

    selected_paths = [
        changed_file.path for changed_file in downloadable_files
    ]

    # A PR's head commit may belong to a contributor's fork.
    download_repository = pull_request.head_repo or repository

    downloaded_files = download_candidate_files(
        repository=download_repository,
        commit_sha=pull_request.head_sha,
        selected_files=selected_paths,
        destination=candidate_workspace,
        token=token,
    )

    report = run_guardian(
        project_root=project_root,
        candidate_root=candidate_workspace,
        selected_files=selected_paths,
        workspace_root=integration_workspace,
        run_quality_checks=False,
    )

    return PullRequestInspectionResult(
        pull_request=pull_request,
        changed_files=changed_files,
        downloaded_files=downloaded_files,
        report=report,
    )
