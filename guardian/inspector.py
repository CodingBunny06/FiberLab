"""Inspect FiberLab modules against their agreed integration contracts."""

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass
class InspectionFinding:
    """Represent one result from a Guardian inspection."""

    status: str
    file: str
    message: str


MODULE_CONTRACTS = {
    "physics/numerical_aperture.py": {
        "calculate_numerical_aperture": ("n_core", "n_cladding"),
        "calculate_critical_angle": ("n_core", "n_cladding"),
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
        "create_attenuation_figure": ("distance_km", "power_mw"),
        "create_signal_waveform_figure": (
            "input_signal",
            "output_signal",
            "time_axis",
        ),
    },
}


def inspect_project(project_root: Path) -> list[InspectionFinding]:
    """Inspect physics and visualization modules against their contracts."""
    findings = []
    expected_locations = {
        function_name: relative_path
        for relative_path, functions in MODULE_CONTRACTS.items()
        for function_name in functions
    }

    for relative_path, expected_functions in MODULE_CONTRACTS.items():
        file_path = project_root / relative_path

        if not file_path.exists():
            findings.append(
                InspectionFinding(
                    "PENDING",
                    relative_path,
                    "Module has not been implemented yet.",
                )
            )
            continue

        try:
            source = file_path.read_text(encoding="utf-8")
            module = ast.parse(source, filename=str(file_path))
        except (SyntaxError, UnicodeDecodeError) as error:
            findings.append(
                InspectionFinding(
                    "FAIL",
                    relative_path,
                    f"Unable to parse module: {error}",
                )
            )
            continue

        definitions = {
            node.name: node
            for node in module.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

        for function_name, expected_parameters in expected_functions.items():
            function = definitions.get(function_name)

            if function is None:
                findings.append(
                    InspectionFinding(
                        "FAIL",
                        relative_path,
                        f"Missing required function: {function_name}.",
                    )
                )
                continue

            actual_parameters = tuple(argument.arg for argument in function.args.args)

            if (
                actual_parameters != expected_parameters
                or function.args.posonlyargs
                or function.args.vararg
                or function.args.kwarg
                or function.args.kwonlyargs
            ):
                findings.append(
                    InspectionFinding(
                        "FAIL",
                        relative_path,
                        (
                            f"{function_name} has an incompatible signature. "
                            f"Expected {expected_parameters}; "
                            f"got {actual_parameters}."
                        ),
                    )
                )
            else:
                findings.append(
                    InspectionFinding(
                        "PASS",
                        relative_path,
                        f"{function_name} matches its expected signature.",
                    )
                )

    # Check for contract functions implemented in the wrong module.
    for package in ("physics", "visualization"):
        package_path = project_root / package

        if not package_path.exists():
            continue

        for file_path in package_path.rglob("*.py"):
            try:
                module = ast.parse(
                    file_path.read_text(encoding="utf-8"),
                    filename=str(file_path),
                )
            except (SyntaxError, UnicodeDecodeError):
                continue

            relative_path = file_path.relative_to(project_root).as_posix()

            for node in module.body:
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue

                expected_path = expected_locations.get(node.name)

                if expected_path and relative_path != expected_path:
                    findings.append(
                        InspectionFinding(
                            "FAIL",
                            relative_path,
                            (
                                f"{node.name} belongs in {expected_path}, "
                                f"not {relative_path}."
                            ),
                        )
                    )

    # Physics and visualization must remain independent of Streamlit.
    for package in ("physics", "visualization"):
        package_path = project_root / package

        if not package_path.exists():
            continue

        for file_path in package_path.rglob("*.py"):
            relative_path = file_path.relative_to(project_root).as_posix()

            try:
                module = ast.parse(
                    file_path.read_text(encoding="utf-8"),
                    filename=str(file_path),
                )
            except (SyntaxError, UnicodeDecodeError):
                continue

            for node in ast.walk(module):
                imports_streamlit = (
                    isinstance(node, ast.Import)
                    and any(alias.name == "streamlit" for alias in node.names)
                ) or (isinstance(node, ast.ImportFrom) and node.module == "streamlit")

                if imports_streamlit:
                    findings.append(
                        InspectionFinding(
                            "FAIL",
                            relative_path,
                            "Streamlit import is not allowed in this package.",
                        )
                    )
    findings.extend(inspect_internal_imports(project_root))
    findings.extend(inspect_package_syntax(project_root, findings))

    return findings


def inspect_internal_imports(project_root: Path) -> list[InspectionFinding]:
    """Detect broken internal module and symbol imports."""
    findings = []
    project_packages = ("physics", "visualization", "components", "pages", "guardian")

    for package in project_packages:
        package_path = project_root / package

        if not package_path.exists():
            continue

        for file_path in package_path.rglob("*.py"):
            relative_path = file_path.relative_to(project_root).as_posix()

            try:
                module = ast.parse(
                    file_path.read_text(encoding="utf-8"),
                    filename=str(file_path),
                )
            except (SyntaxError, UnicodeDecodeError):
                continue

            for node in ast.walk(module):
                if not isinstance(node, ast.ImportFrom) or not node.module:
                    continue

                imported_module = node.module
                root_package = imported_module.split(".")[0]

                if root_package not in project_packages:
                    continue

                module_path = project_root.joinpath(*imported_module.split("."))

                target_file = module_path.with_suffix(".py")
                target_init = module_path / "__init__.py"

                if target_file.exists():
                    pass
                elif target_init.exists():
                    target_file = target_init
                else:
                    findings.append(
                        InspectionFinding(
                            "FAIL",
                            relative_path,
                            f"Broken internal import: {imported_module}.",
                        )
                    )
                    continue

                try:
                    target_source = target_file.read_text(encoding="utf-8")
                    target_ast = ast.parse(
                        target_source,
                        filename=str(target_file),
                    )
                except (SyntaxError, UnicodeDecodeError):
                    continue

                available_symbols = {
                    item.name
                    for item in target_ast.body
                    if isinstance(
                        item,
                        (
                            ast.FunctionDef,
                            ast.AsyncFunctionDef,
                            ast.ClassDef,
                        ),
                    )
                }

                available_symbols.update(
                    item.targets[0].id
                    for item in target_ast.body
                    if isinstance(item, ast.Assign)
                    and len(item.targets) == 1
                    and isinstance(item.targets[0], ast.Name)
                )

                for alias in node.names:
                    if alias.name == "*":
                        continue

                    # Allow imports of submodules.
                    submodule_path = module_path / f"{alias.name}.py"
                    submodule_package = module_path / alias.name / "__init__.py"

                    if (
                        alias.name in available_symbols
                        or submodule_path.exists()
                        or submodule_package.exists()
                    ):
                        continue

                    findings.append(
                        InspectionFinding(
                            "FAIL",
                            relative_path,
                            (
                                f"Missing imported symbol '{alias.name}' "
                                f"in module '{imported_module}'."
                            ),
                        )
                    )

    return findings


def inspect_package_syntax(
    project_root: Path,
    existing_findings: list[InspectionFinding],
) -> list[InspectionFinding]:
    """Detect syntax errors across all application Python packages."""
    findings = []

    already_reported = {
        finding.file
        for finding in existing_findings
        if finding.status == "FAIL" and "Unable to parse module" in finding.message
    }

    for package in ("physics", "visualization", "components", "pages", "guardian"):
        package_path = project_root / package

        if not package_path.exists():
            continue

        for file_path in package_path.rglob("*.py"):
            relative_path = file_path.relative_to(project_root).as_posix()

            if relative_path in already_reported:
                continue

            try:
                source = file_path.read_text(encoding="utf-8")
                ast.parse(source, filename=str(file_path))
            except (SyntaxError, UnicodeDecodeError) as error:
                findings.append(
                    InspectionFinding(
                        "FAIL",
                        relative_path,
                        f"Unable to parse module: {error}",
                    )
                )
    return findings
