"""Optical power attenuation calculations."""

from __future__ import annotations

import math


def _valid(value: float, name: str, *, allow_zero: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number.")
    result = float(value)
    if not math.isfinite(result) or result < 0 or (not allow_zero and result == 0):
        qualifier = "non-negative" if allow_zero else "positive"
        raise ValueError(f"{name} must be finite and {qualifier}.")
    return result


def calculate_total_loss(attenuation_db_per_km: float, length_km: float) -> float:
    """Return total loss in dB."""
    alpha = _valid(attenuation_db_per_km, "attenuation_db_per_km", allow_zero=True)
    length = _valid(length_km, "length_km")
    return alpha * length


def calculate_output_power(
    input_power_mw: float, attenuation_db_per_km: float, length_km: float
) -> float:
    """Return output power in mW using Pout = Pin * 10^(-loss/10)."""
    power = _valid(input_power_mw, "input_power_mw")
    loss = calculate_total_loss(attenuation_db_per_km, length_km)
    return power * (10 ** (-loss / 10))
