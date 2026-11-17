"""Gaussian pulse propagation with second-order dispersion."""
from __future__ import annotations

import math


def broaden_gaussian_pulse(
    time_s: list[float], pulse_width_s: float, beta2_s2_per_km: float, length_km: float
) -> tuple[list[float], list[float], float]:
    """Return time axis, broadened normalized Gaussian, and output RMS width.

    Uses sigma_out = sigma_in * sqrt(1 + (beta2*L/sigma_in**2)**2).
    This is an educational second-order-dispersion model, not a full link budget.
    """
    if not math.isfinite(pulse_width_s) or pulse_width_s <= 0:
        raise ValueError("pulse_width_s must be finite and positive.")
    if not math.isfinite(beta2_s2_per_km):
        raise ValueError("beta2_s2_per_km must be finite.")
    if not math.isfinite(length_km) or length_km < 0:
        raise ValueError("length_km must be finite and non-negative.")
    sigma_out = pulse_width_s * math.sqrt(
        1 + (beta2_s2_per_km * length_km / (pulse_width_s**2)) ** 2
    )
    amplitude = [
        math.exp(-(t * t) / (2 * sigma_out * sigma_out)) for t in time_s
    ]
    return time_s, amplitude, sigma_out
