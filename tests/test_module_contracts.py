
"""Tests for FiberLab module integration contracts."""

import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Expected public APIs and their parameter names, in order.
MODULE_CONTRACTS = {
    "physics/numerical_aperture.py": {
        "calculate_numerical_aperture": (
            "n_core",
            "n_cladding",
        ),
        "calculate_critical_angle": (
            "n_core",
            "n_cladding",
        ),
    },
    "physics/attenuation.py": {
        "calculate_output_power": (
            "input_power_mw",
            "attenuation_db_per_km",
            "length_km",
        ),
        "calculate_total_loss": (
            "attenuation_db_per_km",
            "length_km",
        ),
    },
    "visualization/fiber_animation.py": {
        "create_fiber_ray_figure": ("ray_data",),
    },
    "visualization/signal_graphs.py": {
        "create_attenuation_figure": (
            "distance_km",
            "power_mw",
        ),
        "create_signal_waveform_figure": (
            "input_signal",
            "output_signal",
            "time_axis",
        ),
    },
}


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
    contract = PROJECT_ROOT / "docs" / "integration" / "MODULE_CONTRACTS.md"
    content = contract.read_text(encoding="utf-8")

    assert "calculate_numerical_aperture" in content
    assert "calculate_critical_angle" in content
    assert "calculate_output_power" in content
    assert "calculate_total_loss" in content


def test_visualization_api_contract_exists():
    contract = PROJECT_ROOT / "docs" / "integration" / "MODULE_CONTRACTS.md"
    content = contract.read_text(encoding="utf-8")

    assert "create_fiber_ray_figure" in content
    assert "create_attenuation_figure" in content
    assert "create_signal_waveform_figure" in content


def test_application_integration_contract_exists():
    contract = PROJECT_ROOT / "docs" / "integration" / "MODULE_CONTRACTS.md"
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


def test_implemented_module_api_signatures():
    """Validate implemented APIs without importing or executing modules."""

    expected_locations = {}

    for relative_path, functions in MODULE_CONTRACTS.items():
        expected_path = PROJECT_ROOT / relative_path

        for function_name in functions:
            expected_locations[function_name] = expected_path

        # Not implemented yet: allow the teammate to add it later.
        if not expected_path.exists():
            continue

        source = expected_path.read_text(encoding="utf-8")
        module = ast.parse(source, filename=str(expected_path))

        definitions = {
            node.name: node
            for node in module.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

        for function_name, expected_parameters in functions.items():
            assert function_name in definitions, (
                f"{function_name} is missing from {relative_path}"
            )

            function = definitions[function_name]
            actual_parameters = tuple(
                argument.arg for argument in function.args.args
            )

            assert actual_parameters == expected_parameters, (
                f"{function_name} in {relative_path} has incorrect "
                f"parameters. Expected {expected_parameters}, "
                f"got {actual_parameters}."
            )

            assert not function.args.posonlyargs, (
                f"{function_name} must not use positional-only parameters."
            )
            assert function.args.vararg is None, (
                f"{function_name} must not use *args."
            )
            assert function.args.kwarg is None, (
                f"{function_name} must not use **kwargs."
            )
            assert not function.args.kwonlyargs, (
                f"{function_name} must not use keyword-only parameters."
            )

    # Detect contract functions implemented in the wrong module.
    for package in ("physics", "visualization"):
        package_path = PROJECT_ROOT / package

        for file_path in package_path.glob("*.py"):
            source = file_path.read_text(encoding="utf-8")
            module = ast.parse(source, filename=str(file_path))

            for node in module.body:
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue

                expected_path = expected_locations.get(node.name)

                if expected_path is not None:
                    assert file_path == expected_path, (
                        f"{node.name} belongs in "
                        f"{expected_path.relative_to(PROJECT_ROOT)}, "
                        f"not {file_path.relative_to(PROJECT_ROOT)}."
                    )
