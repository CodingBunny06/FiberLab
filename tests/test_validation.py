"""Tests for FiberLab input validation."""

import pytest

from components.validation import (
    validate_non_negative,
    validate_positive,
    validate_refractive_indices,
)


def test_validate_positive_accepts_valid_value():
    assert validate_positive(5.0, "Length") is None


def test_validate_positive_rejects_zero():
    with pytest.raises(ValueError):
        validate_positive(0, "Length")


def test_validate_positive_rejects_negative():
    with pytest.raises(ValueError):
        validate_positive(-2.0, "Length")


def test_validate_positive_rejects_infinity():
    with pytest.raises(ValueError):
        validate_positive(float("inf"), "Length")


def test_validate_non_negative_accepts_zero():
    assert validate_non_negative(0, "Attenuation") is None


def test_validate_non_negative_rejects_negative():
    with pytest.raises(ValueError):
        validate_non_negative(-1.0, "Attenuation")


def test_validate_refractive_indices_accepts_valid_values():
    assert validate_refractive_indices(1.5, 1.4) is None


def test_validate_refractive_indices_rejects_invalid_order():
    with pytest.raises(ValueError):
        validate_refractive_indices(1.4, 1.5)


@pytest.mark.parametrize("value", ["1.5", None, True, object()])
def test_validate_positive_rejects_non_numeric_values(value):
    with pytest.raises(ValueError):
        validate_positive(value, "Length")


@pytest.mark.parametrize("value", ["0", None, False, object()])
def test_validate_non_negative_rejects_non_numeric_values(value):
    with pytest.raises(ValueError):
        validate_non_negative(value, "Attenuation")
