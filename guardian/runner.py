
"""Coordinate the FiberLab Guardian integration workflow."""

from pathlib import Path

from guardian.error_detector import Diagnostic, analyze_findings
from guardian.inspector import inspect_project
from guardian.integration_engine import (
    create_integration_workspace,
    integrate_candidate_modules,
)
from guardian.reporter import (
    GuardianReport,
)
from guardian.test_runner import CommandResult, run_command


def run_guardian(
    project_root: Path,
    candidate_root: Path,
    selected_files: list[str],
    workspace_root: Path,
    run_quality_checks: bool = True,
    timeout_seconds: int = 120,
) -> GuardianReport:
    """Integrate candidate modules, inspect the workspace and run quality checks."""

    create_integration_workspace(project_root, workspace_root)

    integrate_candidate_modules(
        candidate_root,
        workspace_root,
        selected_files,
    )

    findings = inspect_project(workspace_root)
    diagnostics = analyze_findings(findings)

    passed = sum(item.status == "PASS" for item in diagnostics)
    failed = sum(item.status == "FAIL" for item in diagnostics)
    pending = sum(item.status == "PENDING" for item in diagnostics)

    if failed:
        return GuardianReport(
            diagnostics=diagnostics,
            passed=passed,
            failed=failed,
            pending=pending,
        )

    
    
    if run_quality_checks:
        commands = [
            ["ruff", "check", "."],
            ["python", "-m", "pytest", "-v"],
        ]

        for command in commands:
            result = run_command(
                command,
                workspace_root,
                timeout_seconds,
            )

            diagnostic = _command_diagnostic(result)
            diagnostics.append(diagnostic)

            if result.status == "PASS":
                passed += 1
            else:
                failed += 1

    return GuardianReport(
        diagnostics=diagnostics,
        passed=passed,
        failed=failed,
        pending=pending,
    )

def _command_diagnostic(result: CommandResult):
    """Convert an automated command result into a Guardian diagnostic."""

    return Diagnostic(
        status="PASS" if result.status == "PASS" else "FAIL",
        severity="INFO" if result.status == "PASS" else "HIGH",
        file="integration workspace",
        message=(
            f"Automated check: {result.status} "
            f"(exit code: {result.return_code})"
        ),
        recommendation=(
            "No action required."
            if result.status == "PASS"
            else result.stderr or result.stdout or "Review the command failure."
        ),
    )
