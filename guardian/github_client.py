
"""Read-only GitHub API client for FiberLab Guardian."""

import json
import os
import re
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass
class PullRequestInfo:
    """Metadata describing a GitHub pull request."""

    number: int
    title: str
    state: str
    base_branch: str
    head_branch: str
    head_sha: str
    head_repo: str | None


@dataclass
class ChangedFile:
    """File changed by a GitHub pull request."""

    path: str
    status: str
    additions: int
    deletions: int
    changes: int


class GitHubAPIError(Exception):
    """Raised when a GitHub API request fails."""


class GitHubClient:
    """Read-only client for retrieving GitHub pull request data."""

    API_URL = "https://api.github.com"
    API_VERSION = "2022-11-28"

    def __init__(self, token: str | None = None, timeout: int = 15):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.timeout = timeout

    @staticmethod
    def _validate_repository(repository: str) -> None:
        if not isinstance(repository, str) or not re.fullmatch(
            r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",
            repository,
        ):
            raise ValueError("Repository must use the owner/repository format.")

    @staticmethod
    def _validate_pr_number(pr_number: int) -> None:
        if (
            isinstance(pr_number, bool)
            or not isinstance(pr_number, int)
            or pr_number <= 0
        ):
            raise ValueError("Pull request number must be a positive integer.")

    def _request(self, endpoint: str) -> dict | list:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": self.API_VERSION,
            "User-Agent": "FiberLab-Guardian",
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        request = Request(
            f"{self.API_URL}{endpoint}",
            headers=headers,
            method="GET",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))

        except HTTPError as error:
            if error.code == 404:
                raise GitHubAPIError("GitHub resource was not found.") from error

            if error.code == 401:
                raise GitHubAPIError("GitHub authentication failed.") from error

            if error.code == 403:
                raise GitHubAPIError(
                    "GitHub access was denied or rate-limited."
                ) from error

            raise GitHubAPIError(
                f"GitHub API returned HTTP {error.code}."
            ) from error

        except (URLError, TimeoutError, OSError) as error:
            raise GitHubAPIError(
                "Unable to connect to the GitHub API."
            ) from error

        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise GitHubAPIError(
                "GitHub returned an invalid JSON response."
            ) from error

    def get_pull_request(
        self,
        repository: str,
        pr_number: int,
    ) -> PullRequestInfo:
        """Retrieve pull request metadata."""

        self._validate_repository(repository)
        self._validate_pr_number(pr_number)

        data = self._request(
            f"/repos/{repository}/pulls/{pr_number}"
        )

        if not isinstance(data, dict):
            raise GitHubAPIError("Unexpected pull request response.")

        head = data.get("head") or {}
        base = data.get("base") or {}
        head_repo = head.get("repo")

        return PullRequestInfo(
            number=data["number"],
            title=data["title"],
            state=data["state"],
            base_branch=base["ref"],
            head_branch=head["ref"],
            head_sha=head["sha"],
            head_repo=(
                head_repo.get("full_name")
                if isinstance(head_repo, dict)
                else None
            ),
        )

    def list_changed_files(
        self,
        repository: str,
        pr_number: int,
    ) -> list[ChangedFile]:
        """Retrieve every file changed by a pull request."""

        self._validate_repository(repository)
        self._validate_pr_number(pr_number)

        files = []
        page = 1

        while True:
            data = self._request(
                f"/repos/{repository}/pulls/{pr_number}/files"
                f"?per_page=100&page={page}"
            )

            if not isinstance(data, list):
                raise GitHubAPIError("Unexpected changed-files response.")

            for item in data:
                files.append(
                    ChangedFile(
                        path=item["filename"],
                        status=item["status"],
                        additions=item["additions"],
                        deletions=item["deletions"],
                        changes=item["changes"],
                    )
                )

            if len(data) < 100:
                break

            page += 1

        return files
