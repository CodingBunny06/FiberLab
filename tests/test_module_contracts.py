
"""Tests for FiberLab module integration contracts."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_physics_package_exists():
    assert (PROJECT_ROOT / "physics" / "__init__.py").exists()


def test_visualization_package_exists():
    assert (PROJECT_ROOT / "visualization" / "__init__.py").exists()


def test_integration_contract_document_exists():
    assert (
        PROJECT_ROOT / "docs" / "integration" / "MODULE_CONTRACTS.md"
    ).exists()


def test_physics_package_does_not_import_streamlit():
    physics_files = list((PROJECT_ROOT / "physics").glob("*.py"))

    for file_path in physics_files:
        source = file_path.read_text(encoding="utf-8")
        assert "import streamlit" not in source
        assert "from streamlit" not in source


def test_physics_api_contract_exists():
    contract = (
        PROJECT_ROOT / "docs" / "integration" / "MODULE_CONTRACTS.md"
    )
    content = contract.read_text(encoding="utf-8")

    assert "calculate_numerical_aperture" in content
    assert "calculate_critical_angle" in content
    assert "calculate_output_power" in content
    assert "calculate_total_loss" in content


def test_visualization_api_contract_exists():
    contract = (
        PROJECT_ROOT / "docs" / "integration" / "MODULE_CONTRACTS.md"
    )
    content = contract.read_text(encoding="utf-8")

    assert "create_fiber_ray_figure" in content
    assert "create_attenuation_figure" in content
    assert "create_signal_waveform_figure" in content


def test_application_integration_contract_exists():
    contract = (
        PROJECT_ROOT / "docs" / "integration" / "MODULE_CONTRACTS.md"
    )
    content = contract.read_text(encoding="utf-8")

    assert "Application Integration API" in content
    assert "Error Handling" in content


def test_visualization_package_does_not_import_streamlit():
    visualization_files = list(
        (PROJECT_ROOT / "visualization").glob("*.py")
    )

    for file_path in visualization_files:
        source = file_path.read_text(encoding="utf-8")
        assert "import streamlit" not in source
        assert "from streamlit" not in source
