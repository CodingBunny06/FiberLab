
# FiberLab Module Integration Contracts

## 1. Purpose

This document defines how the physics, visualization, and Streamlit application modules communicate.

All modules must follow these conventions to ensure smooth integration.

## 2. General Conventions

- Python is the implementation language.
- SI units are used internally wherever practical.
- UI input conversions must happen at the application boundary.
- Physics calculations must not depend on Streamlit.
- Visualization functions must receive calculated data rather than independently implementing physics.
- Functions must have clear names, type hints, and docstrings.
- Invalid inputs must raise appropriate exceptions.

## 3. Physics Module Contract

Location: `physics/`

Responsibilities:
- Optical fiber calculations.
- Numerical aperture and acceptance angle.
- Critical angle and total internal reflection.
- Optical attenuation.
- Basic signal propagation and pulse broadening.

Expected conventions:
- Functions accept numerical inputs.
- Functions return numerical results or structured result objects.
- Internal units must be documented.
- Physics calculations must be independently testable.

## 4. Visualization Module Contract

Location: `visualization/`

Responsibilities:
- Fiber ray visualizations.
- Optical power graphs.
- Signal waveform graphs.
- Pulse broadening visualizations.

Expected conventions:
- Visualization functions receive inputs or results from the physics module.
- Plotly figures should be returned for Streamlit rendering.
- Visualization code must not duplicate physics calculations.

## 5. Application Integration Contract

Location: `app.py`, `pages/`, and `components/`

Responsibilities:
- Collect user inputs.
- Validate UI values.
- Convert UI units into internal units.
- Call physics functions.
- Pass calculated results to visualization functions.
- Display results and explanations.

Streamlit must remain in the application and presentation layers.

## 6. Testing Requirements

- Physics functions require unit tests.
- Visualization functions require appropriate output tests.
- Application pages require rendering and integration tests.
- All pull requests must pass Ruff and Pytest checks.

## 7. Collaboration Rules

- Each team member works on their assigned feature branch.
- Shared interfaces must be agreed upon before implementation.
- Changes must be submitted through pull requests.
- Do not modify another member's assigned modules without coordination.


## 8. Physics API — Function Specifications

The physics module provides numerical calculations independently of Streamlit.

### 8.1 Numerical Aperture

File: `physics/numerical_aperture.py`

Function:
```python
def calculate_numerical_aperture(n_core: float, n_cladding: float) -> float: ...
```

Inputs:
- `n_core`: Core refractive index (dimensionless).
- `n_cladding`: Cladding refractive index (dimensionless).

Output:
- Numerical aperture (dimensionless).

Assumption:
- The v1.0 calculation assumes the external medium is air
  (refractive index n_external = 1.0).
- Therefore, the numerical aperture is calculated as:

  NA = sqrt(n_core² - n_cladding²)

- Supporting other external media may be considered in a future version.

### 8.2 Critical Angle

File: `physics/numerical_aperture.py`

Function:
```python
def calculate_critical_angle(n_core: float, n_cladding: float) -> float: ...
```

Output:
- Critical angle in radians.

### 8.3 Attenuation

File: `physics/attenuation.py`

Function:
```python
def calculate_output_power(
    input_power_mw: float, attenuation_db_per_km: float, length_km: float
) -> float: ...
```

Output:
- Output optical power in mW.

### 8.4 Total Power Loss

File: `physics/attenuation.py`

Function:
```python
def calculate_total_loss(attenuation_db_per_km: float, length_km: float) -> float: ...
```

Output:
- Total attenuation in dB.

### 8.5 General Requirements

- Validate all input values.
- Require `n_core > n_cladding > 0`.
- Require positive optical power and fiber length.
- Require non-negative attenuation.
- Raise `ValueError` for invalid inputs.
- Use radians internally for angle calculations.
- Include type hints and docstrings.
- Write independent unit tests for every function.

These signatures define the proposed v1.0 interface. Implementation remains the responsibility of the physics module owner.



## 9. Visualization API — Function Specifications

The visualization module converts simulation data into interactive visual outputs.

### 9.1 Fiber Ray Visualization

File: `visualization/fiber_animation.py`

Proposed function:

```python
def create_fiber_ray_figure(ray_data): ...
```

### 9.2 Attenuation Graph

File: `visualization/signal_graphs.py`

Proposed function:

```python
def create_attenuation_figure(distance_km, power_mw): ...
```

### 9.3 Signal Waveform Graph

File: `visualization/signal_graphs.py`

Proposed function:

```python
def create_signal_waveform_figure(input_signal, output_signal, time_axis): ...
```

Output:
- Plotly Figure comparing input and output waveforms.

Additional requirements:
- Input waveform, output waveform, and time-axis arrays must have compatible lengths.
- The exact data types and units must be agreed upon before implementation.

### 9.4 General Requirements

- Use Plotly for interactive graphs.
- Return Plotly Figure objects.
- Do not implement independent physics calculations.
- Receive calculated values or simulation data from the physics module.
- Include axis labels, units, legends and meaningful titles.
- Handle empty or invalid input data appropriately.
- Include tests for figure creation and output structure.

These signatures are proposed v1.0 interfaces. The visualization module owner must review and agree to them before implementation.



## 10. Application Integration API

The application layer connects user inputs, physics calculations, and visualizations.

### 10.1 Responsibilities

The application layer must:

1. Collect inputs from the user through Streamlit.
2. Validate input values.
3. Convert UI units into internal units.
4. Call the relevant physics functions.
5. Pass calculated results to visualization functions.
6. Display numerical results, graphs, and explanations.

### 10.2 Fiber Explorer

Page: `pages/fiber_explorer.py`

Integration flow:

User inputs
→ Physics calculations
→ Numerical results
→ Fiber visualization
→ Streamlit display

Expected calculations:
- Numerical aperture
- Critical angle
- Acceptance angle
- Total internal reflection conditions

### 10.3 Attenuation Laboratory

Page: `pages/attenuation_laboratory.py`

Integration flow:

Input power and fiber parameters
→ Attenuation calculations
→ Output power and total loss
→ Attenuation graph
→ Streamlit display

### 10.4 Signal Propagation

Page: `pages/signal_propagation.py`

Integration flow:

Input waveform and fiber parameters
→ Signal propagation model
→ Output waveform
→ Input/output comparison graph
→ Streamlit display

### 10.5 Error Handling

- Display understandable error messages for invalid user inputs.
- Do not allow invalid values to reach physics calculations.
- Handle calculation errors without crashing the application.
- Keep error handling separate from physics calculations.

### 10.6 Architectural Rules

- `app.py` controls application navigation.
- `pages/` handles user interaction and orchestration.
- `physics/` handles scientific calculations.
- `visualization/` handles graphical representations.
- `components/` contains reusable UI components.
- Physics and visualization modules must not depend on Streamlit.
