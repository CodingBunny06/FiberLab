# FiberLab v1.0.0 — Release Notes (Draft)

> Draft only. Confirm every item against the final merged implementation before publishing.

## Overview

FiberLab is a Streamlit-based optical-fiber learning and simulation project. Version 1.0 is intended to provide a modular application structure for exploring optical-fiber concepts, with separate physics, visualization, and application layers.

## Intended v1.0 feature areas

- Fiber Explorer
- Attenuation Laboratory
- Basic Signal Propagation
- Learning Lab

## Architecture

- `physics/` — scientific calculations and simulation models.
- `visualization/` — Plotly-based visual representations of calculated data.
- `pages/` — Streamlit page-level interaction and orchestration.
- `components/` — reusable UI components.
- `guardian/` — project inspection and integration-support workflows.

## Validation record

Add the exact release-candidate commit SHA and verified results before publishing:

- Ruff lint:
- Ruff format:
- Pytest:
- Manual application walkthrough:
- CI run:

## Known limitations

Document functionality that is incomplete, simplified, or deferred. Do not claim dispersion, modulation, BER, SNR, or eye-diagram capabilities unless those models are implemented and validated.

## Contributors

Add the final contributor list and contributions after confirming the merged work.
