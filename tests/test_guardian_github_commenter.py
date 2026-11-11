
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


def sample_report():
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


def test_formats_guardian_report_as_markdown():
    comment = format_guardian_comment(sample_report())

    assert "FiberLab Guardian Report" in comment
    assert "FAIL" in comment
    assert "Passed: **1**" in comment
    assert "Failed: **1**" in comment
    assert "Pending: **1**" in comment
    assert "physics/numerical_aperture.py" in comment
    assert "Check the module contract." in comment


def test_rejects_invalid_repository():
    with pytest.raises(ValueError):
        publish_guardian_comment(
            "invalid-repository",
            12,
            sample_report(),
            token="test-token",
        )


def test_rejects_invalid_pr_number():
    with pytest.raises(ValueError):
        publish_guardian_comment(
            "CodingBunny06/FiberLab",
            0,
            sample_report(),
            token="test-token",
        )


def test_rejects_missing_token(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    with pytest.raises(ValueError, match="GitHub token"):
        publish_guardian_comment(
            "CodingBunny06/FiberLab",
            12,
            sample_report(),
        )


def test_publishes_comment_successfully(monkeypatch):
    response_data = {
        "id": 12345,
        "html_url": "https://github.com/CodingBunny06/FiberLab/pull/12#issuecomment-12345",
    }

    def mock_urlopen(request, timeout):
        assert request.get_method() == "POST"
        assert request.get_header("Authorization") == "Bearer test-token"
        assert request.get_header("Content-type") == "application/json"
        assert "/issues/12/comments" in request.full_url

        body = json.loads(request.data.decode("utf-8"))
        assert "FiberLab Guardian Report" in body["body"]

        return io.BytesIO(json.dumps(response_data).encode("utf-8"))

    monkeypatch.setattr(
        "guardian.github_commenter.urlopen",
        mock_urlopen,
    )

    result = publish_guardian_comment(
        "CodingBunny06/FiberLab",
        12,
        sample_report(),
        token="test-token",
    )

    assert result.comment_id == 12345
    assert result.comment_url == response_data["html_url"]


def test_handles_github_http_error(monkeypatch):
    def mock_urlopen(request, timeout):
        raise HTTPError(
            request.full_url,
            403,
            "Forbidden",
            None,
            None,
        )

    monkeypatch.setattr(
        "guardian.github_commenter.urlopen",
        mock_urlopen,
    )

    with pytest.raises(
        GitHubCommentError,
        match="denied comment publishing",
    ):
        publish_guardian_comment(
            "CodingBunny06/FiberLab",
            12,
            sample_report(),
            token="test-token",
        )


def test_handles_network_error(monkeypatch):
    def mock_urlopen(request, timeout):
        raise URLError("Connection unavailable")

    monkeypatch.setattr(
        "guardian.github_commenter.urlopen",
        mock_urlopen,
    )

    with pytest.raises(GitHubCommentError, match="connect"):
        publish_guardian_comment(
            "CodingBunny06/FiberLab",
            12,
            sample_report(),
            token="test-token",
        )
