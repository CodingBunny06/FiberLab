"""Tests for the Guardian GitHub candidate downloader."""

import io
from urllib.error import HTTPError, URLError

import pytest

from guardian.candidate_downloader import (
    CandidateDownloadError,
    download_candidate_files,
)

REPOSITORY = "CodingBunny06/FiberLab"
COMMIT_SHA = "a" * 40


def test_downloads_candidate_file(monkeypatch, tmp_path):
    content = b"def calculate_output_power():\n    return 10\n"

    def mock_urlopen(request, timeout, context):
        assert COMMIT_SHA in request.full_url
        return io.BytesIO(content)

    monkeypatch.setattr(
        "guardian.candidate_downloader.urlopen",
        mock_urlopen,
    )

    destination = tmp_path / "candidate"

    downloaded = download_candidate_files(
        REPOSITORY,
        COMMIT_SHA,
        ["physics/attenuation.py"],
        destination,
    )

    expected_file = destination / "physics" / "attenuation.py"

    assert downloaded == [expected_file]
    assert expected_file.read_bytes() == content


def test_downloads_multiple_candidate_files(monkeypatch, tmp_path):
    responses = [b"first file", b"second file"]

    def mock_urlopen(request, timeout, context):
        return io.BytesIO(responses.pop(0))

    monkeypatch.setattr(
        "guardian.candidate_downloader.urlopen",
        mock_urlopen,
    )

    destination = tmp_path / "candidate"

    downloaded = download_candidate_files(
        REPOSITORY,
        COMMIT_SHA,
        ["physics/attenuation.py", "visualization/signal_graphs.py"],
        destination,
    )

    assert len(downloaded) == 2
    assert downloaded[0].read_bytes() == b"first file"
    assert downloaded[1].read_bytes() == b"second file"


def test_rejects_path_traversal(tmp_path):
    destination = tmp_path / "candidate"

    with pytest.raises(ValueError):
        download_candidate_files(
            REPOSITORY,
            COMMIT_SHA,
            ["../outside.py"],
            destination,
        )

    assert not destination.exists()


def test_refuses_existing_destination(monkeypatch, tmp_path):
    destination = tmp_path / "candidate"
    destination.mkdir()

    with pytest.raises(FileExistsError):
        download_candidate_files(
            REPOSITORY,
            COMMIT_SHA,
            ["physics/attenuation.py"],
            destination,
        )


def test_handles_github_http_error(monkeypatch, tmp_path):
    def mock_urlopen(request, timeout, context):
        raise HTTPError(
            request.full_url,
            404,
            "Not Found",
            None,
            None,
        )

    monkeypatch.setattr(
        "guardian.candidate_downloader.urlopen",
        mock_urlopen,
    )

    with pytest.raises(CandidateDownloadError):
        download_candidate_files(
            REPOSITORY,
            COMMIT_SHA,
            ["physics/attenuation.py"],
            tmp_path / "candidate",
        )


def test_handles_network_error(monkeypatch, tmp_path):
    def mock_urlopen(request, timeout, context):
        raise URLError("Connection unavailable")

    monkeypatch.setattr(
        "guardian.candidate_downloader.urlopen",
        mock_urlopen,
    )

    with pytest.raises(CandidateDownloadError):
        download_candidate_files(
            REPOSITORY,
            COMMIT_SHA,
            ["physics/attenuation.py"],
            tmp_path / "candidate",
        )


def test_rejects_invalid_commit_sha(tmp_path):
    with pytest.raises(ValueError):
        download_candidate_files(
            REPOSITORY,
            "invalid-sha",
            ["physics/attenuation.py"],
            tmp_path / "candidate",
        )


def test_rejects_absolute_file_path(tmp_path):
    with pytest.raises(ValueError):
        download_candidate_files(
            REPOSITORY,
            COMMIT_SHA,
            ["/tmp/outside.py"],
            tmp_path / "candidate",
        )
