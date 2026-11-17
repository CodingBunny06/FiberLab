import math

import pytest

from visualization.matter_wave import (
    MAX_RENDERED_CYCLES,
    create_matter_wave_figure,
)


def test_matter_wave_uses_fixed_physical_distance():
    figure = create_matter_wave_figure(1e-9, 5.0, 0.75)

    assert figure.data[0].x[0] == pytest.approx(0)
    assert figure.data[0].x[-1] == pytest.approx(5.0)
    assert figure.layout.xaxis.title.text == "Physical position (nm)"


def test_shorter_wavelength_produces_more_cycles_in_same_window():
    electron_like = create_matter_wave_figure(1e-9, 5.0, 0.75)
    proton_like = create_matter_wave_figure(0.5e-9, 5.0, 0.75)

    assert len(proton_like.data[0].x) > len(electron_like.data[0].x)


def test_matter_wave_rejects_unrenderable_cycle_count():
    with pytest.raises(ValueError, match="wave cycles"):
        create_matter_wave_figure(1e-12, 10.0, 0.75)


@pytest.mark.parametrize(
    "wavelength,window,amplitude",
    [(0, 1, 1), (1e-9, 0, 1), (1e-9, 1, math.inf), (True, 1, 1)],
)
def test_matter_wave_rejects_invalid_inputs(wavelength, window, amplitude):
    with pytest.raises(ValueError):
        create_matter_wave_figure(wavelength, window, amplitude)
