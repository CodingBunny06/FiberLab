"""Tests for the FiberLab Guardian code inspector."""

from pathlib import Path

from guardian.inspector import inspect_project


def create_module(root: Path, relative_path: str, source: str) -> None:
    """Create a Python module inside a temporary project."""
    file_path = root / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(source, encoding="utf-8")


def test_missing_modules_are_reported_as_pending(tmp_path):
    findings = inspect_project(tmp_path)

    assert findings
    assert all(finding.status == "PENDING" for finding in findings)


def test_valid_physics_module_passes_signature_check(tmp_path):
    create_module(
        tmp_path,
        "physics/numerical_aperture.py",
        """
def calculate_numerical_aperture(n_core, n_cladding):
    return 0.0

def calculate_critical_angle(n_core, n_cladding):
    return 0.0
""",
    )

    findings = inspect_project(tmp_path)

    assert any(
        finding.status == "PASS" and "calculate_numerical_aperture" in finding.message
        for finding in findings
    )


def test_incorrect_signature_is_detected(tmp_path):
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

    findings = inspect_project(tmp_path)

    assert any(
        finding.status == "FAIL" and "incompatible signature" in finding.message
        for finding in findings
    )


def test_syntax_error_is_detected(tmp_path):
    create_module(
        tmp_path,
        "physics/numerical_aperture.py",
        "def calculate_numerical_aperture(:",
    )

    findings = inspect_project(tmp_path)

    assert any(
        finding.status == "FAIL" and "Unable to parse module" in finding.message
        for finding in findings
    )


def test_streamlit_import_is_detected(tmp_path):
    create_module(
        tmp_path,
        "physics/numerical_aperture.py",
        """
import streamlit

def calculate_numerical_aperture(n_core, n_cladding):
    return 0.0

def calculate_critical_angle(n_core, n_cladding):
    return 0.0
""",
    )

    findings = inspect_project(tmp_path)

    assert any(
        finding.status == "FAIL" and "Streamlit import" in finding.message
        for finding in findings
    )


def test_missing_function_is_detected(tmp_path):
    create_module(
        tmp_path,
        "physics/numerical_aperture.py",
        """
def calculate_numerical_aperture(n_core, n_cladding):
    return 0.0
""",
    )

    findings = inspect_project(tmp_path)

    assert any(
        finding.status == "FAIL" and "calculate_critical_angle" in finding.message
        for finding in findings
    )


def test_function_in_wrong_module_is_detected(tmp_path):
    create_module(
        tmp_path,
        "physics/attenuation.py",
        """
def calculate_numerical_aperture(n_core, n_cladding):
    return 0.0
""",
    )

    findings = inspect_project(tmp_path)

    assert any(
        finding.status == "FAIL"
        and "belongs in physics/numerical_aperture.py" in finding.message
        for finding in findings
    )


def test_missing_internal_module_import_is_detected(tmp_path):
    create_module(
        tmp_path,
        "physics/numerical_aperture.py",
        """
from physics.missing_module import calculate_something

def calculate_numerical_aperture(n_core, n_cladding):
    return 0.0

def calculate_critical_angle(n_core, n_cladding):
    return 0.0
""",
    )

    findings = inspect_project(tmp_path)

    assert any(
        finding.status == "FAIL" and "physics.missing_module" in finding.message
        for finding in findings
    )


def test_missing_imported_function_is_detected(tmp_path):
    create_module(
        tmp_path,
        "physics/attenuation.py",
        """
def calculate_output_power(input_power_mw, attenuation_db_per_km, length_km):
    return 1.0
""",
    )

    create_module(
        tmp_path,
        "visualization/signal_graphs.py",
        """
from physics.attenuation import calculate_loss
""",
    )

    findings = inspect_project(tmp_path)

    assert any(
        finding.status == "FAIL" and "calculate_loss" in finding.message
        for finding in findings
    )


def test_syntax_error_in_non_contract_module_is_detected(tmp_path):
    create_module(
        tmp_path,
        "visualization/helpers.py",
        "def create_figure(:",
    )

    findings = inspect_project(tmp_path)

    assert any(
        finding.status == "FAIL"
        and finding.file == "visualization/helpers.py"
        and "Unable to parse module" in finding.message
        for finding in findings
    )


def test_streamlit_import_in_nested_module_is_detected(tmp_path):
    create_module(
        tmp_path,
        "visualization/helpers/renderer.py",
        "import streamlit",
    )

    findings = inspect_project(tmp_path)

    assert any(
        finding.status == "FAIL"
        and finding.file == "visualization/helpers/renderer.py"
        and "Streamlit import" in finding.message
        for finding in findings
    )


def test_contract_function_in_nested_module_is_detected(tmp_path):
    create_module(
        tmp_path,
        "physics/helpers/numerical.py",
        """
def calculate_numerical_aperture(n_core, n_cladding):
    return 0.0
""",
    )

    findings = inspect_project(tmp_path)

    assert any(
        finding.status == "FAIL"
        and finding.file == "physics/helpers/numerical.py"
        and "belongs in physics/numerical_aperture.py" in finding.message
        for finding in findings
    )



def test_syntax_error_in_guardian_module_is_detected(tmp_path):
    create_module(
        tmp_path,
        "guardian/helpers.py",
        "def inspect_candidate(:",
    )

    findings = inspect_project(tmp_path)

    assert any(
        finding.status == "FAIL"
        and finding.file == "guardian/helpers.py"
        and "Unable to parse module" in finding.message
        for finding in findings
    )
