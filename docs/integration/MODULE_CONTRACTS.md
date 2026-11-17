# FiberLab module contracts — implemented interfaces

## Application Integration API

The Streamlit pages coordinate user inputs, physics calculations, and Plotly figures. The application router is defined in `app.py`.

## Separation of concerns
- `physics/` contains numerical calculations and simulation models. It must not import Streamlit or Plotly.
- `visualization/` receives prepared numerical data and returns Plotly figures. It must not depend on Streamlit.
- `pages/` collects user input, calls physics functions, and renders figures.
- SI units are used in physics APIs unless a function name or docstring states otherwise.

## Physics APIs

### Optical fiber
- `calculate_numerical_aperture(n_core, n_cladding) -> float`
- `calculate_critical_angle(n_core, n_cladding) -> float` (radians from interface normal)
- `calculate_acceptance_angle(n_core, n_cladding) -> float` (radians from fiber axis; air outside)
- `is_total_internal_reflection(incidence_angle, critical_angle) -> bool`
- `simulate_fiber_ray(n_core, n_cladding, core_radius_um=25, cladding_radius_um=62.5, length_um=500, launch_angle_deg=8, samples=400) -> dict`

### De Broglie matter waves
- `de_broglie_wavelength(mass_kg, velocity_m_s) -> float` (metres; non-relativistic)
- `momentum(mass_kg, velocity_m_s) -> float` (kg m/s; non-relativistic)
- `wavelength_from_momentum(momentum_kg_m_s) -> float` (metres)

The matter-wave page labels the sinusoid as an illustrative spatial periodicity, not a particle trajectory or a full quantum wavefunction.

### Attenuation
- `calculate_total_loss(attenuation_db_per_km, length_km) -> float` (dB)
- `calculate_output_power(input_power_mw, attenuation_db_per_km, length_km) -> float` (mW)

### Signal propagation
- `broaden_gaussian_pulse(time_s, pulse_width_s, beta2_s2_per_km, length_km)`
  returns the supplied time axis, normalized output pulse, and output RMS width in seconds. This is a simplified educational second-order-dispersion model.

## Visualization APIs
- `create_fiber_ray_figure(ray_data) -> plotly.graph_objects.Figure`
- `create_attenuation_figure(distance_km, power_mw) -> Figure`
- `create_signal_waveform_figure(input_signal, output_signal, time_axis) -> Figure`

## Validation
Physics functions reject invalid physical ranges and non-finite values. UI pages should show user-readable errors rather than allowing invalid inputs to crash the application. Tests cover calculation references, boundaries, invalid inputs, module signatures, visualization output, and navigation.
