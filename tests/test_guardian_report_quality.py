"""Tests for Guardian report quality and diagnostics."""

from guardian.error_detector import Diagnostic
from guardian.reporter import GuardianReport, format_report


def test_report_prioritizes_failure_over_pending():
    report = GuardianReport(
        diagnostics=[],
        passed=2,
        failed=1,
        pending=3,
    )

    assert report.overall_status == "FAIL"


def test_report_returns_pending_when_no_failures():
    report = GuardianReport(
        diagnostics=[],
        passed=2,
        failed=0,
        pending=3,
    )

    assert report.overall_status == "PENDING"


def test_report_returns_pass_when_no_failures_or_pending():
    report = GuardianReport(
        diagnostics=[],
        passed=5,
        failed=0,
        pending=0,
    )

    assert report.overall_status == "PASS"


def test_formatted_report_contains_diagnostic_details():
    diagnostic = Diagnostic(
        status="FAIL",
        severity="HIGH",
        file="physics/numerical_aperture.py",
        message="Function signature does not match the contract.",
        recommendation="Update the function signature.",
    )

    report = GuardianReport(
        diagnostics=[diagnostic],
        passed=2,
        failed=1,
        pending=0,
    )

    output = format_report(report)

    assert "FAIL" in output
    assert "physics/numerical_aperture.py" in output
    assert "HIGH" in output
    assert "Function signature does not match the contract." in output
    assert "Update the function signature." in output
