"""Classify and explain findings produced by FiberLab Guardian."""

from dataclasses import dataclass

from guardian.inspector import InspectionFinding


@dataclass
class Diagnostic:
    """Represent an actionable Guardian diagnostic."""

    status: str
    severity: str
    file: str
    message: str
    recommendation: str


def classify_finding(finding: InspectionFinding) -> Diagnostic:
    """Convert an inspection finding into an actionable diagnostic."""
    if finding.status == "PASS":
        return Diagnostic(
            "PASS",
            "INFO",
            finding.file,
            finding.message,
            "No action required.",
        )

    if finding.status == "PENDING":
        return Diagnostic(
            "PENDING",
            "WAITING",
            finding.file,
            finding.message,
            "Wait for the module owner to submit the implementation.",
        )

    message = finding.message.lower()

    recommendations = (
        (
            "unable to parse module",
            "Fix the Python syntax error in this file.",
        ),
        (
            "missing required function",
            "Implement the missing function according to MODULE_CONTRACTS.md.",
        ),
        (
            "incompatible signature",
            "Update the function parameters to match the agreed API contract.",
        ),
        (
            "broken internal import",
            "Check the import path and ensure the target module exists.",
        ),
        (
            "missing imported symbol",
            "Define the missing function or class in the imported module.",
        ),
        (
            "streamlit import",
            "Move Streamlit-dependent code into the application layer.",
        ),
        (
            "belongs in",
            "Move the function to the module specified by the integration contract.",
        ),
    )

    recommendation = "Review the finding and compare the implementation with the integration contract."

    for keyword, action in recommendations:
        if keyword in message:
            recommendation = action
            break

    return Diagnostic(
        "FAIL",
        "HIGH",
        finding.file,
        finding.message,
        recommendation,
    )


def analyze_findings(
    findings: list[InspectionFinding],
) -> list[Diagnostic]:
    """Classify all findings produced by the Code Inspector."""
    return [classify_finding(finding) for finding in findings]
