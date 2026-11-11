
"""Tests for the FiberLab Guardian error detector."""

from guardian.error_detector import analyze_findings, classify_finding
from guardian.inspector import InspectionFinding


def test_pass_finding_is_classified_as_info():
    finding = InspectionFinding("PASS", "physics/test.py", "API is valid.")

    diagnostic = classify_finding(finding)

    assert diagnostic.severity == "INFO"
    assert diagnostic.recommendation == "No action required."


def test_pending_finding_is_classified_as_waiting():
    finding = InspectionFinding(
        "PENDING",
        "physics/test.py",
        "Module is not implemented.",
    )

    diagnostic = classify_finding(finding)

    assert diagnostic.severity == "WAITING"
    assert diagnostic.status == "PENDING"


def test_missing_function_gets_recommendation():
    finding = InspectionFinding(
        "FAIL",
        "physics/attenuation.py",
        "Missing required function: calculate_output_power.",
    )

    diagnostic = classify_finding(finding)

    assert diagnostic.severity == "HIGH"
    assert "Implement the missing function" in diagnostic.recommendation


def test_broken_import_gets_recommendation():
    finding = InspectionFinding(
        "FAIL",
        "visualization/signal_graphs.py",
        "Broken internal import: physics.missing_module.",
    )

    diagnostic = classify_finding(finding)

    assert "import path" in diagnostic.recommendation


def test_multiple_findings_are_classified():
    findings = [
        InspectionFinding("PASS", "physics/test.py", "Valid."),
        InspectionFinding("PENDING", "visualization/test.py", "Pending."),
        InspectionFinding("FAIL", "physics/test.py", "Syntax error."),
    ]

    diagnostics = analyze_findings(findings)

    assert len(diagnostics) == 3
    assert [item.status for item in diagnostics] == [
        "PASS",
        "PENDING",
        "FAIL",
    ]
