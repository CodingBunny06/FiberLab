import io
import json
from urllib.error import HTTPError, URLError

import pytest

from guardian.github_client import (
    ChangedFile,
    GitHubAPIError,
    GitHubClient,
    PullRequestInfo,
)


def test_pull_request_info_stores_metadata():
    pull_request = PullRequestInfo(
        number=12,
        title="Implement attenuation module",
        state="open",
        base_branch="main",
        head_branch="feature/attenuation",
        head_sha="abc123",
        head_repo="CodingBunny06/FiberLab",
    )

    assert pull_request.number == 12
    assert pull_request.title == "Implement attenuation module"
    assert pull_request.state == "open"
    assert pull_request.base_branch == "main"
    assert pull_request.head_branch == "feature/attenuation"
    assert pull_request.head_sha == "abc123"


def test_changed_file_stores_change_details():
    changed_file = ChangedFile(
        path="physics/attenuation.py",
        status="added",
        additions=25,
        deletions=0,
        changes=25,
    )

    assert changed_file.path == "physics/attenuation.py"
    assert changed_file.status == "added"
    assert changed_file.additions == 25
    assert changed_file.deletions == 0
    assert changed_file.changes == 25


def test_github_client_rejects_invalid_repository():
    client = GitHubClient()

    with pytest.raises(ValueError):
        client.get_pull_request("invalid-repository", 12)


def test_github_client_rejects_invalid_pr_number():
    client = GitHubClient()

    with pytest.raises(ValueError):
        client.get_pull_request(
            "CodingBunny06/FiberLab",
            0,
        )

def test_github_client_rejects_boolean_pr_number():
    client = GitHubClient()

    with pytest.raises(ValueError):
        client.get_pull_request(
            "CodingBunny06/FiberLab",
            True,
        )


def test_github_client_rejects_malformed_repository():
    client = GitHubClient()

    with pytest.raises(ValueError):
        client.get_pull_request(
            "CodingBunny06/FiberLab/extra",
            12,
        )

def test_get_pull_request_retrieves_metadata_and_uses_token(monkeypatch):
    """Verify PR metadata retrieval and authentication."""

    response_data = {
        "number": 12,
        "title": "Implement attenuation module",
        "state": "open",
        "base": {"ref": "main"},
        "head": {
            "ref": "feature/attenuation",
            "sha": "abc123",
            "repo": {"full_name": "CodingBunny06/FiberLab"},
        },
    }

    def mock_urlopen(request, timeout):
        assert request.get_header("Authorization") == "Bearer test-token"
        assert timeout == 15
        return io.BytesIO(json.dumps(response_data).encode("utf-8"))

    monkeypatch.setattr("guardian.github_client.urlopen", mock_urlopen)

    client = GitHubClient(token="test-token")
    result = client.get_pull_request("CodingBunny06/FiberLab", 12)

    assert result.number == 12
    assert result.title == "Implement attenuation module"
    assert result.head_sha == "abc123"
    assert result.head_branch == "feature/attenuation"


def test_list_changed_files_handles_pagination(monkeypatch):
    """Verify changed files are retrieved across multiple API pages."""

    first_page = [
        {
            "filename": f"physics/module_{index}.py",
            "status": "added",
            "additions": 10,
            "deletions": 0,
            "changes": 10,
        }
        for index in range(100)
    ]

    second_page = [
        {
            "filename": "physics/attenuation.py",
            "status": "modified",
            "additions": 5,
            "deletions": 2,
            "changes": 7,
        }
    ]

    responses = [first_page, second_page]
    requested_urls = []

    def mock_urlopen(request, timeout):
        requested_urls.append(request.full_url)
        return io.BytesIO(
            json.dumps(responses.pop(0)).encode("utf-8")
        )

    monkeypatch.setattr("guardian.github_client.urlopen", mock_urlopen)

    client = GitHubClient()
    files = client.list_changed_files("CodingBunny06/FiberLab", 12)

    assert len(files) == 101
    assert files[-1].path == "physics/attenuation.py"
    assert "page=1" in requested_urls[0]
    assert "page=2" in requested_urls[1]


def test_github_client_handles_http_errors(monkeypatch):
    """Verify GitHub HTTP errors are converted into API errors."""

    def mock_urlopen(request, timeout):
        raise HTTPError(
            request.full_url,
            404,
            "Not Found",
            None,
            None,
        )

    monkeypatch.setattr("guardian.github_client.urlopen", mock_urlopen)

    client = GitHubClient()

    with pytest.raises(GitHubAPIError, match="not found"):
        client.get_pull_request("CodingBunny06/FiberLab", 12)


def test_github_client_handles_network_errors(monkeypatch):
    """Verify network failures are handled cleanly."""

    def mock_urlopen(request, timeout):
        raise URLError("Connection unavailable")

    monkeypatch.setattr("guardian.github_client.urlopen", mock_urlopen)

    client = GitHubClient()

    with pytest.raises(GitHubAPIError, match="Unable to connect"):
        client.get_pull_request("CodingBunny06/FiberLab", 12)
