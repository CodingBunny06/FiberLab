"""Core step-index optical-fiber calculations.

Angles returned by this module are in radians.  The incidence angle used by
``is_total_internal_reflection`` is measured from the interface normal.
"""

import math
from numbers import Real


def _validate_refractive_indices(n_core: float, n_cladding: float) -> None:
    """Validate refractive indices for a core-cladding interface."""
    if (
        isinstance(n_core, bool)
        or isinstance(n_cladding, bool)
        or not isinstance(n_core, Real)
        or not isinstance(n_cladding, Real)
        or not math.isfinite(n_core)
        or not math.isfinite(n_cladding)
        or n_core <= n_cladding
        or n_cladding <= 0
    ):
        raise ValueError("Require finite refractive indices n_core > n_cladding > 0.")


def _validate_angle(angle: float, name: str, *, allow_zero: bool = True) -> None:
    """Validate an angle measured in radians at an optical interface."""
    if (
        isinstance(angle, bool)
        or not isinstance(angle, Real)
        or not math.isfinite(angle)
        or angle < 0
        or angle > math.pi / 2
        or (not allow_zero and angle == 0)
    ):
        raise ValueError(f"{name} must be a finite angle in the range (0, pi/2].")


def calculate_numerical_aperture(n_core: float, n_cladding: float) -> float:
    """Return the dimensionless numerical aperture for air outside the fiber.

    The step-index relation is ``NA = sqrt(n_core**2 - n_cladding**2)``.
    Refractive indices are dimensionless and must satisfy
    ``n_core > n_cladding > 0``.
    """
    _validate_refractive_indices(n_core, n_cladding)
    return math.sqrt(n_core**2 - n_cladding**2)


def calculate_critical_angle(n_core: float, n_cladding: float) -> float:
    """Return the core-cladding critical angle in radians.

    The angle is measured from the normal to the interface and is
    ``asin(n_cladding / n_core)``.
    """
    _validate_refractive_indices(n_core, n_cladding)
    return math.asin(n_cladding / n_core)


def calculate_acceptance_angle(n_core: float, n_cladding: float) -> float:
    """Return the maximum air acceptance angle from the fiber axis, in radians.

    For an external medium of air (refractive index 1), this is
    ``asin(NA)``.  A numerical aperture greater than one cannot produce a
    real acceptance angle in air and is rejected rather than clipped.
    """
    numerical_aperture = calculate_numerical_aperture(n_core, n_cladding)
    if numerical_aperture > 1:
        raise ValueError("Numerical aperture must not exceed one for air.")
    return math.asin(numerical_aperture)


def is_total_internal_reflection(incidence_angle: float, critical_angle: float) -> bool:
    """Return whether an incidence angle produces total internal reflection.

    Both angles are in radians and measured from the interface normal.
    TIR occurs strictly when ``incidence_angle > critical_angle``; equality
    is the limiting grazing-refraction case, not TIR.
    """
    _validate_angle(incidence_angle, "Incidence angle")
    _validate_angle(critical_angle, "Critical angle", allow_zero=False)
    return incidence_angle > critical_angle
