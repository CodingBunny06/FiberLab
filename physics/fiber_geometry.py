"""Step-index fiber ray-path simulation helpers."""

from __future__ import annotations

import math

from physics.numerical_aperture import (
    calculate_acceptance_angle,
    calculate_critical_angle,
    calculate_numerical_aperture,
)


def simulate_fiber_ray(
    n_core: float,
    n_cladding: float,
    core_radius_um: float = 25.0,
    cladding_radius_um: float = 62.5,
    length_um: float = 500.0,
    launch_angle_deg: float = 8.0,
    samples: int = 400,
) -> dict:
    """Generate a meridional ray path and metadata for the ray visualizer.

    The launch angle is measured from the fiber axis. A guided ray reflects
    specularly at the core boundary; a non-guided ray is shown exiting into
    the cladding. Coordinates are illustrative geometrical optics.
    """
    values = (core_radius_um, cladding_radius_um, length_um)
    if any(not math.isfinite(v) or v <= 0 for v in values):
        raise ValueError("Fiber dimensions must be finite and positive.")
    if cladding_radius_um <= core_radius_um:
        raise ValueError("Cladding radius must exceed core radius.")
    if samples < 20:
        raise ValueError("samples must be at least 20.")
    na = calculate_numerical_aperture(n_core, n_cladding)
    acceptance = calculate_acceptance_angle(n_core, n_cladding)
    critical = calculate_critical_angle(n_core, n_cladding)
    angle = math.radians(launch_angle_deg)
    if not math.isfinite(angle) or angle < 0 or angle >= math.pi / 2:
        raise ValueError("Launch angle must be between 0 and 90 degrees.")
    guided = angle <= acceptance
    x = [length_um * i / (samples - 1) for i in range(samples)]
    slope = math.tan(angle)
    y = []
    for position in x:
        raw = position * slope
        if guided:
            period = 4 * core_radius_um
            folded = (raw + core_radius_um) % period
            y.append(
                -core_radius_um + folded
                if folded <= 2 * core_radius_um
                else 3 * core_radius_um - folded
            )
        else:
            y.append(raw)
    incident = {"x": [-max(core_radius_um, 10.0), 0.0], "y": [0.0, 0.0]}
    result = {
        "core_radius": core_radius_um,
        "cladding_radius": cladding_radius_um,
        "fiber_length": length_um,
        "incident_ray": incident,
        "propagating_ray": {"x": x, "y": y},
        "is_tir": guided,
        "n_core": n_core,
        "n_cladding": n_cladding,
        "incident_angle_deg": launch_angle_deg,
        "acceptance_angle_deg": math.degrees(acceptance),
        "critical_angle_deg": math.degrees(critical),
        "numerical_aperture": na,
    }
    if not guided:
        exit_x = min(length_um, core_radius_um / max(slope, 1e-12))
        result["refracted_ray"] = {
            "x": [0.0, exit_x],
            "y": [0.0, min(cladding_radius_um, exit_x * slope)],
        }
    return result
