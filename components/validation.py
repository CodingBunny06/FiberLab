"""Input validation utilities for FiberLab."""

import math


def validate_positive(value: float, name: str) -> None:
    """Ensure a value is finite and greater than zero."""
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a finite positive number.")


def validate_non_negative(value: float, name: str) -> None:
    """Ensure a value is finite and non-negative."""
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be a finite non-negative number.")


def validate_refractive_indices(
    n_core: float,
    n_cladding: float,
) -> None:
    """Validate core and cladding refractive indices."""
    validate_positive(n_core, "Core refractive index")
    validate_positive(n_cladding, "Cladding refractive index")

    if n_core <= n_cladding:
        raise ValueError(
            "Core refractive index must be greater than cladding refractive index."
        )
