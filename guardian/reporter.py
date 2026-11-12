"""Generate consolidated reports from FiberLab Guardian inspections."""

from dataclasses import dataclass
from pathlib import Path

from guardian.error_detector import Diagnostic, analyze_findings
from guardian.inspector import inspect_project


@dataclass
class GuardianReport:
    """Store the complete results of a Guardian inspection."""

    diagnostics: list[Diagnostic]
    passed: int
    failed: int
    pending: int

    @property
    def overall_status(self) -> str:
        """Determine the overall inspection status."""
        if self.failed:
            return "FAIL"

        if self.pending:
            return "PENDING"

        return "PASS"


def generate_report(project_root: Path) -> GuardianReport:
    """Run inspection, classify findings, and generate a report."""
    findings = inspect_project(project_root)
    diagnostics = analyze_findings(findings)

    return GuardianReport(
        diagnostics=diagnostics,
        passed=sum(item.status == "PASS" for item in diagnostics),
        failed=sum(item.status == "FAIL" for item in diagnostics),
        pending=sum(item.status == "PENDING" for item in diagnostics),
    )


def format_report(report: GuardianReport) -> str:
    """Format a Guardian report into a readable diagnostic summary."""

    lines = [
        "FIBERLAB GUARDIAN REPORT",
        "=" * 40,
        "",
        f"Overall Status: {report.overall_status}",
        "",
        "SUMMARY",
        "-" * 40,
        f"Passed:  {report.passed}",
        f"Failed:  {report.failed}",
        f"Pending: {report.pending}",
        "",
        "DIAGNOSTICS",
        "-" * 40,
    ]

    if not report.diagnostics:
        lines.append("No diagnostics available.")
    else:
        for index, diagnostic in enumerate(report.diagnostics, start=1):
            lines.extend(
                [
                    "",
                    f"{index}. [{diagnostic.status}] {diagnostic.file}",
                    f"   Severity: {diagnostic.severity}",
                    f"   Finding: {diagnostic.message}",
                    f"   Recommendation: {diagnostic.recommendation}",
                ]
            )

    lines.extend(
        [
            "",
            "=" * 40,
            "End of Guardian Report",
        ]
    )

    return "\n".join(lines)
