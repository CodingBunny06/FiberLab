"""Tests for Guardian GitHub PR comment publishing."""

import io
import json
from urllib.error import HTTPError, URLError

import pytest

from guardian.error_detector import Diagnostic
from guardian.github_commenter import (
    GitHubCommentError,
    format_guardian_comment,
    publish_guardian_comment,
)
from guardian.reporter import GuardianReport

REPOSITORY = "CodingBunny06/FiberLab"
PR_NUMBER = 12
TEST_TOKEN = "test-token"

VALID_COMMENT_URL = (
    "https://github.com/CodingBunny06/FiberLab/pull/12#issuecomment-12345"
)


def sample_report():
    """Create a representative Guardian report."""
    return GuardianReport(
        diagnostics=[
            Diagnostic(
                status="PASS",
                severity="INFO",
                file="physics/attenuation.py",
                message="Required function found.",
                recommendation="No action required.",
            ),
            Diagnostic(
                status="FAIL",
                severity="HIGH",
                file="physics/numerical_aperture.py",
                message="Incorrect function signature.",
                recommendation="Check the module contract.",
            ),
            Diagnostic(
                status="PENDING",
                severity="WAITING",
                file="visualization/signal_graphs.py",
                message="Required module is missing.",
                recommendation="Wait for the module owner.",
            ),
        ],
        passed=1,
        failed=1,
        pending=1,
    )


def mock_successful_response():
    """Create a mock successful GitHub API response."""
    response_data = {
        "id": 12345,
        "html_url": VALID_COMMENT_URL,
    }

    return io.BytesIO(json.dumps(response_data).encode("utf-8"))


def test_formats_guardian_report_as_markdown():
    comment = format_guardian_comment(sample_report())

    assert "FiberLab Guardian Report" in comment
    assert "FAIL" in comment
    assert "Passed: **1**" in comment
    assert "Failed: **1**" in comment
    assert "Pending: **1**" in comment
    assert "physics/numerical_aperture.py" in comment
    assert "Check the module contract." in comment
    assert "not an approval or merge decision" in comment


def test_formats_report_without_diagnostics():
    report = GuardianReport(
        diagnostics=[],
        passed=0,
        failed=0,
        pending=0,
    )

    comment = format_guardian_comment(report)

    assert "No diagnostic findings were generated." in comment


def test_rejects_oversized_report():
    report = GuardianReport(
        diagnostics=[
            Diagnostic(
                status="FAIL",
                severity="HIGH",
                file="large_file.py",
                message="x" * 61_000,
                recommendation="Review the file.",
            )
        ],
        passed=0,
        failed=1,
        pending=0,
    )

    with pytest.raises(ValueError, match="too long"):
        format_guardian_comment(report)


@pytest.mark.parametrize(
    "repository",
    [
        "invalid-repository",
        "",
        "owner/",
        "/repository",
        "owner/repository/extra",
        "owner/repo name",
        None,
    ],
)
def test_rejects_invalid_repository(repository):
    with pytest.raises(ValueError):
        publish_guardian_comment(
            repository,
            PR_NUMBER,
            sample_report(),
            token=TEST_TOKEN,
        )


@pytest.mark.parametrize(
    "pr_number",
    [0, -1, True, False, 1.5, "12"],
)
def test_rejects_invalid_pr_number(pr_number):
    with pytest.raises(ValueError):
        publish_guardian_comment(
            REPOSITORY,
            pr_number,
            sample_report(),
            token=TEST_TOKEN,
        )


@pytest.mark.parametrize(
    "timeout",
    [0, -1, True, False, 1.5, "15"],
)
def test_rejects_invalid_timeout(timeout):
    with pytest.raises(ValueError, match="Timeout"):
        publish_guardian_comment(
            REPOSITORY,
            PR_NUMBER,
            sample_report(),
            token=TEST_TOKEN,
            timeout=timeout,
        )


def test_rejects_missing_token(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    with pytest.raises(ValueError, match="GitHub token"):
        publish_guardian_comment(
            REPOSITORY,
            PR_NUMBER,
            sample_report(),
        )


@pytest.mark.parametrize("token", ["", " ", "   ", None])
def test_rejects_empty_token(token, monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    if token is None:
        pytest.skip("None means use the environment variable.")

    with pytest.raises(ValueError, match="GitHub token"):
        publish_guardian_comment(
            REPOSITORY,
            PR_NUMBER,
            sample_report(),
            token=token,
        )


def test_rejects_token_with_surrounding_whitespace():
    with pytest.raises(ValueError, match="surrounding whitespace"):
        publish_guardian_comment(
            REPOSITORY,
            PR_NUMBER,
            sample_report(),
            token=" test-token ",
        )


def test_uses_environment_token(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", TEST_TOKEN)

    def mock_urlopen(request, timeout, context):
        assert request.get_header("Authorization") == f"Bearer {TEST_TOKEN}"
        return mock_successful_response()

    monkeypatch.setattr(
        "guardian.github_commenter.urlopen",
        mock_urlopen,
    )

    result = publish_guardian_comment(
        REPOSITORY,
        PR_NUMBER,
        sample_report(),
    )

    assert result.comment_id == 12345


def test_publishes_comment_successfully(monkeypatch):
    def mock_urlopen(request, timeout, context):
        assert request.get_method() == "POST"
        assert request.get_header("Authorization") == f"Bearer {TEST_TOKEN}"
        assert request.get_header("Content-type") == "application/json"
        assert request.get_header("Accept") == "application/vnd.github+json"
        assert request.get_header("X-github-api-version") == "2022-11-28"
        assert f"/issues/{PR_NUMBER}/comments" in request.full_url
        assert timeout == 15
        assert context is not None

        body = json.loads(request.data.decode("utf-8"))
        assert "FiberLab Guardian Report" in body["body"]

        return mock_successful_response()

    monkeypatch.setattr(
        "guardian.github_commenter.urlopen",
        mock_urlopen,
    )

    result = publish_guardian_comment(
        REPOSITORY,
        PR_NUMBER,
        sample_report(),
        token=TEST_TOKEN,
    )

    assert result.comment_id == 12345
    assert result.comment_url == VALID_COMMENT_URL


@pytest.mark.parametrize(
    "invalid_url",
    [
        "http://github.com/owner/repo",
        "https://evil.example.com/comment",
        "https://github.com.evil.example.com/comment",
        "https://evil@github.com/comment",
        "https://github.com:444/comment",
        "not-a-url",
        "",
    ],
)
def test_rejects_invalid_comment_url(monkeypatch, invalid_url):
    response_data = {
        "id": 12345,
        "html_url": invalid_url,
    }

    def mock_urlopen(request, timeout, context):
        return io.BytesIO(json.dumps(response_data).encode("utf-8"))

    monkeypatch.setattr(
        "guardian.github_commenter.urlopen",
        mock_urlopen,
    )

    with pytest.raises(GitHubCommentError, match="unexpected comment response"):
        publish_guardian_comment(
            REPOSITORY,
            PR_NUMBER,
            sample_report(),
            token=TEST_TOKEN,
        )


@pytest.mark.parametrize(
    "response_data",
    [
        {},
        {"html_url": VALID_COMMENT_URL},
        {"id": 12345},
        {"id": True, "html_url": VALID_COMMENT_URL},
        {"id": "12345", "html_url": VALID_COMMENT_URL},
        [],
        None,
    ],
)
def test_rejects_incomplete_or_invalid_response(monkeypatch, response_data):
    def mock_urlopen(request, timeout, context):
        return io.BytesIO(json.dumps(response_data).encode("utf-8"))

    monkeypatch.setattr(
        "guardian.github_commenter.urlopen",
        mock_urlopen,
    )

    with pytest.raises(GitHubCommentError, match="unexpected comment response"):
        publish_guardian_comment(
            REPOSITORY,
            PR_NUMBER,
            sample_report(),
            token=TEST_TOKEN,
        )


def test_handles_malformed_json_response(monkeypatch):
    def mock_urlopen(request, timeout, context):
        return io.BytesIO(b"{invalid json")

    monkeypatch.setattr(
        "guardian.github_commenter.urlopen",
        mock_urlopen,
    )

    with pytest.raises(GitHubCommentError, match="invalid comment response"):
        publish_guardian_comment(
            REPOSITORY,
            PR_NUMBER,
            sample_report(),
            token=TEST_TOKEN,
        )


def test_handles_invalid_unicode_response(monkeypatch):
    def mock_urlopen(request, timeout, context):
        return io.BytesIO(b"\xff\xfe")

    monkeypatch.setattr(
        "guardian.github_commenter.urlopen",
        mock_urlopen,
    )

    with pytest.raises(GitHubCommentError, match="invalid comment response"):
        publish_guardian_comment(
            REPOSITORY,
            PR_NUMBER,
            sample_report(),
            token=TEST_TOKEN,
        )


def test_handles_github_http_error(monkeypatch):
    def mock_urlopen(request, timeout, context):
        raise HTTPError(
            request.full_url,
            403,
            "Forbidden",
            None,
            io.BytesIO(b'{"message": "Resource not accessible"}'),
        )

    monkeypatch.setattr(
        "guardian.github_commenter.urlopen",
        mock_urlopen,
    )

    with pytest.raises(
        GitHubCommentError,
        match="HTTP 403.*Resource not accessible",
    ):
        publish_guardian_comment(
            REPOSITORY,
            PR_NUMBER,
            sample_report(),
            token=TEST_TOKEN,
        )


def test_handles_unreadable_github_error_response(monkeypatch):
    def mock_urlopen(request, timeout, context):
        raise HTTPError(
            request.full_url,
            500,
            "Internal Server Error",
            None,
            io.BytesIO(b"not json"),
        )

    monkeypatch.setattr(
        "guardian.github_commenter.urlopen",
        mock_urlopen,
    )

    with pytest.raises(
        GitHubCommentError,
        match="HTTP 500.*unreadable error response",
    ):
        publish_guardian_comment(
            REPOSITORY,
            PR_NUMBER,
            sample_report(),
            token=TEST_TOKEN,
        )


def test_handles_network_error(monkeypatch):
    def mock_urlopen(request, timeout, context):
        raise URLError("Connection unavailable")

    monkeypatch.setattr(
        "guardian.github_commenter.urlopen",
        mock_urlopen,
    )

    with pytest.raises(GitHubCommentError, match="connect"):
        publish_guardian_comment(
            REPOSITORY,
            PR_NUMBER,
            sample_report(),
            token=TEST_TOKEN,
        )


def test_handles_timeout(monkeypatch):
    def mock_urlopen(request, timeout, context):
        raise TimeoutError("Request timed out")

    monkeypatch.setattr(
        "guardian.github_commenter.urlopen",
        mock_urlopen,
    )

    with pytest.raises(GitHubCommentError, match="connect"):
        publish_guardian_comment(
            REPOSITORY,
            PR_NUMBER,
            sample_report(),
            token=TEST_TOKEN,
        )
