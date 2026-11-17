# FiberLab 🔬

**Interactive Physics & Optical Fiber Simulation Laboratory**

[![CI](https://github.com/CodingBunny06/FiberLab/actions/workflows/ci.yml/badge.svg)](https://github.com/CodingBunny06/FiberLab/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.67.0-red.svg)](https://streamlit.io/)

FiberLab is a Streamlit-based educational application that turns physics concepts into interactive calculations and visual experiments. It brings together an optical-fiber laboratory and a separate De Broglie matter-wave experiment.

## Live application

**[Open FiberLab](https://fiberlab-xjlvqbfj8kskptzbwddwwc.streamlit.app/)**

## Modules

| Module | What you can explore |
|---|---|
| Fiber Explorer | Step-index fiber parameters, numerical aperture, acceptance angle, critical angle, and guided/escaping ray visualization |
| De Broglie Matter Waves | Matter-wave wavelength calculator, particle presets, physical-distance wave visualization, particle wavelength comparison, and wavelength-versus-velocity graph |
| Attenuation Laboratory | Output power and total-loss calculations, with a power-versus-distance graph |
| Signal Propagation | Gaussian pulse input/output comparison using a second-order dispersion model |
| Guardian | Repository inspection and integration-support dashboard |

## Run locally

Python 3.12 is recommended.

```bash
git clone https://github.com/CodingBunny06/FiberLab.git
cd FiberLab
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit (normally http://localhost:8501).

On Windows, activate the environment with `.venv\\Scripts\\activate`.

## Run checks

```bash
ruff check .
ruff format --check .
python -m pytest -v
```

## Scientific models and assumptions

### De Broglie matter waves

The calculator uses the non-relativistic relation:

`λ = h / p = h / (mv)`

The matter-wave graph uses a selectable physical distance in nanometres, so the number of visible oscillations changes with the calculated wavelength. A separate logarithmic comparison chart compares electron, proton and neutron wavelengths at the selected speed. The sinusoid is an educational illustration of spatial periodicity, not a particle trajectory or a complete quantum wavefunction. The UI warns when the selected speed exceeds 0.1c, where relativistic corrections become increasingly relevant. Extremely dense wave patterns are not plotted when they exceed the rendering limit.

### Optical fiber

The fiber model assumes a step-index fiber and air as the external medium. Angles are documented in the physics module; the acceptance angle is measured from the fiber axis and the critical angle from the interface normal. Ray paths are educational geometrical-optics illustrations.

### Attenuation

The attenuation model uses `Pout = Pin × 10^(-αL/10)`. Connector, splice and bending losses are excluded. At zero distance, the plotted power equals the input power.

### Signal propagation

The signal page uses an educational Gaussian pulse broadening relation with second-order dispersion. It is not a full electromagnetic or optical-link simulation.

## Project layout

- `app.py` — Streamlit navigation and entry point
- `pages/` — user-facing interactive laboratories
- `physics/` — pure calculation and simulation models
- `visualization/` — Plotly figures, independent of Streamlit
- `components/` — reusable UI components
- `guardian/` — Guardian inspection and integration tools
- `tests/` — unit, contract and application tests
- `docs/` — integration and developer documentation

## Security note

Guardian includes GitHub pull-request inspection and an optional action that can publish a report as a PR comment. Do not expose a GitHub token through a public deployment's shared secrets. PR inspection should remain static for untrusted contributions; do not execute untrusted PR code.

See [SECURITY.md](SECURITY.md) for Guardian's security model and known limitations.

## Project status

FiberLab is deployed on Streamlit Community Cloud. The merged `main` branch has passed the project's automated CI checks, and the application has been launched successfully from the local repository.

## Academic presentation note

For the professor's requested demonstration, focus on **De Broglie Matter Waves**. The optical-fiber experiments remain separate modules within the same FiberLab application and need not be included in that focused presentation or report.
