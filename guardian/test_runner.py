"""Run automated quality checks for FiberLab Guardian."""

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CommandResult:
    """Store the result of an executed command."""

    status: str
    return_code: int | None
    stdout: str
    stderr: str


def run_command(
    command: list[str],
    workspace_root: Path,
    timeout_seconds: int = 120,
) -> CommandResult:
    """Execute a command inside the isolated integration workspace."""
    try:
        completed = subprocess.run(
            command,
            cwd=workspace_root,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )

        status = "PASS" if completed.returncode == 0 else "FAIL"

        return CommandResult(
            status=status,
            return_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

    except subprocess.TimeoutExpired as error:
        stdout = error.stdout or ""
        stderr = error.stderr or ""

        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="replace")

        if isinstance(stderr, bytes):
            stderr = stderr.decode(errors="replace")

        return CommandResult(
            status="TIMEOUT",
            return_code=None,
            stdout=stdout,
            stderr=stderr or "Command exceeded its execution timeout.",
        )

    except OSError as error:
        return CommandResult(
            status="ERROR",
            return_code=None,
            stdout="",
            stderr=str(error),
        )
