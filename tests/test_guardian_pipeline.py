
"""End-to-end tests for the FiberLab Guardian pipeline."""

from guardian.reporter import generate_report


def create_module(root, relative_path, source):
    """Create a simulated teammate module."""
    file_path = root / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(source, encoding="utf-8")


def test_guardian_detects_multiple_integration_problems(tmp_path):
    # Simulate a teammate submitting an incorrect physics module.
    create_module(
        tmp_path,
        "physics/numerical_aperture.py",
        """
def calculate_numerical_aperture(n_core, cladding_index):
    return 0.0

def calculate_critical_angle(n_core, n_cladding):
    return 0.0
""",
    )

    # Simulate an invalid import and forbidden dependency.
    create_module(
        tmp_path,
        "visualization/signal_graphs.py",
        """
import streamlit
from physics.numerical_aperture import calculate_missing_function
""",
    )

    report = generate_report(tmp_path)

    failed_messages = [
        diagnostic.message.lower()
        for diagnostic in report.diagnostics
        if diagnostic.status == "FAIL"
    ]

    assert report.overall_status == "FAIL"

    assert any("incompatible signature" in message for message in failed_messages)
    assert any("missing imported symbol" in message for message in failed_messages)
    assert any("streamlit import" in message for message in failed_messages)

    assert report.failed >= 3
    assert report.pending > 0
