import pytest

from physics.attenuation import calculate_output_power, calculate_total_loss


def test_attenuation_reference():
    assert calculate_total_loss(0.2, 10) == pytest.approx(2.0)
    assert calculate_output_power(1.0, 0.2, 10) == pytest.approx(10 ** -0.2)


def test_zero_attenuation_preserves_power():
    assert calculate_output_power(2.5, 0, 10) == pytest.approx(2.5)


@pytest.mark.parametrize("power,alpha,length", [(0, 1, 1), (-1, 1, 1), (1, -1, 1), (1, 1, 0)])
def test_invalid_attenuation_inputs(power, alpha, length):
    with pytest.raises(ValueError):
        calculate_output_power(power, alpha, length)
