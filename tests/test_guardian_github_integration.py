
"""Tests for GitHub pull request integration."""


import pytest

from guardian.github_client import ChangedFile, PullRequestInfo
from guardian.github_integration import inspect_pull_request
from guardian.reporter import GuardianReport


def test_inspects_pull_request_using_existing_guardian_pipeline(
    monkeypatch,
    tmp_path,
):
    """Verify the complete orchestration without network access."""

    pull_request = PullRequestInfo(
        number=12,
        title="Implement attenuation module",
        state="open",
        base_branch="main",
        head_branch="feature/attenuation",
        head_sha="a" * 40,
        head_repo="contributor/FiberLab",
    )

    changed_files = [
        ChangedFile(
            "physics/attenuation.py", "modified", 20, 5, 25
        ),
        ChangedFile(
            "physics/old_module.py", "removed", 0, 10, 10
        ),
    ]

    class FakeGitHubClient:
        def __init__(self, token=None):
            assert token == "test-token"

        def get_pull_request(self, repository, pr_number):
            assert repository == "CodingBunny06/FiberLab"
            assert pr_number == 12
            return pull_request

        def list_changed_files(self, repository, pr_number):
            return changed_files

    downloaded_path = tmp_path / "candidate" / "physics" / "attenuation.py"
    expected_report = GuardianReport(
        diagnostics=[],
        passed=1,
        failed=0,
        pending=2,
    )

    download_calls = {}
    runner_calls = {}

    def fake_download(**kwargs):
        download_calls.update(kwargs)
        return [downloaded_path]

    def fake_runner(**kwargs):
        runner_calls.update(kwargs)
        return expected_report

    monkeypatch.setattr(
        "guardian.github_integration.GitHubClient",
        FakeGitHubClient,
    )
    monkeypatch.setattr(
        "guardian.github_integration.download_candidate_files",
        fake_download,
    )
    monkeypatch.setattr(
        "guardian.github_integration.run_guardian",
        fake_runner,
    )

    result = inspect_pull_request(
        repository="CodingBunny06/FiberLab",
        pr_number=12,
        project_root=tmp_path / "project",
        candidate_workspace=tmp_path / "candidate",
        integration_workspace=tmp_path / "integration",
        token="test-token",
    )

    assert result.pull_request.number == 12
    assert len(result.changed_files) == 2
    assert result.downloaded_files == [downloaded_path]
    assert result.report is expected_report

    assert download_calls["repository"] == "contributor/FiberLab"
    assert download_calls["commit_sha"] == "a" * 40
    assert download_calls["selected_files"] == [
        "physics/attenuation.py"
    ]

    assert runner_calls["selected_files"] == [
        "physics/attenuation.py"
    ]
    assert runner_calls["run_quality_checks"] is False


def test_rejects_pull_request_without_downloadable_files(
    monkeypatch,
    tmp_path,
):
    """Verify deleted-only PRs do not start a download."""

    class FakeGitHubClient:
        def __init__(self, token=None):
            pass

        def get_pull_request(self, repository, pr_number):
            return PullRequestInfo(
                number=13,
                title="Remove old module",
                state="open",
                base_branch="main",
                head_branch="feature/removal",
                head_sha="b" * 40,
                head_repo="contributor/FiberLab",
            )

        def list_changed_files(self, repository, pr_number):
            return [
                ChangedFile(
                    "physics/old_module.py",
                    "removed",
                    0,
                    10,
                    10,
                )
            ]

    def unexpected_download(**kwargs):
        pytest.fail("Downloader should not run for deleted-only PRs.")

    monkeypatch.setattr(
        "guardian.github_integration.GitHubClient",
        FakeGitHubClient,
    )
    monkeypatch.setattr(
        "guardian.github_integration.download_candidate_files",
        unexpected_download,
    )

    with pytest.raises(ValueError, match="no downloadable files"):
        inspect_pull_request(
            repository="CodingBunny06/FiberLab",
            pr_number=13,
            project_root=tmp_path / "project",
            candidate_workspace=tmp_path / "candidate",
            integration_workspace=tmp_path / "integration",
        )
