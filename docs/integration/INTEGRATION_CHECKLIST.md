# FiberLab v1.0 Integration Checklist

Mark an item complete only after verifying it against implementation and test evidence.

## A. Contract agreement
- [ ] Physics owner reviewed and agreed to Section 8 of `MODULE_CONTRACTS.md`.
- [ ] Visualization owner reviewed and agreed to Section 9.
- [ ] Function names, parameters, return types, units, and exceptions are confirmed.
- [ ] Ray-data and waveform-data structures have documented examples.
- [ ] Unit conversions occur at the application boundary.

## B. Physics integration
- [ ] Physics modules import without Streamlit.
- [ ] Numerical-aperture and critical-angle functions match the agreed contract.
- [ ] Attenuation functions match the agreed contract.
- [ ] Signal-propagation outputs have documented units and compatible dimensions.
- [ ] Invalid inputs raise documented exceptions.
- [ ] Unit tests cover normal, boundary, and invalid inputs.

## C. Visualization integration
- [ ] Visualization consumes calculated data and does not reimplement physics.
- [ ] Fiber-ray function accepts the agreed ray-data structure.
- [ ] Attenuation graph receives compatible distance and power arrays.
- [ ] Signal graph receives compatible input, output, and time-axis arrays.
- [ ] Functions return Plotly Figure objects.
- [ ] Empty and invalid data are handled predictably.
- [ ] Tests inspect figure type, traces, labels, and data.

## D. Application integration
- [ ] `app.py` owns navigation.
- [ ] Pages call the agreed physics API and pass results to the agreed visualization API.
- [ ] UI values are validated before calculations.
- [ ] UI-to-SI conversions occur at the application boundary.
- [ ] Errors are shown clearly without crashing the application.
- [ ] Physics and visualization modules do not depend on Streamlit.

## E. Feature walkthrough
- [ ] Fiber Explorer: numerical aperture, critical angle, acceptance angle, and TIR conditions.
- [ ] Attenuation Laboratory: output power, total loss, and graph.
- [ ] Signal Propagation: input/output signal flow and comparison graph.
- [ ] Learning Lab: educational content and navigation.
- [ ] Navigation between all pages works.
- [ ] Valid, invalid, boundary, and empty inputs are exercised.

## F. Final evidence
- [ ] Full test suite passes on the final integration commit.
- [ ] Ruff lint and format checks pass.
- [ ] CI passes on the exact commit proposed for merge.
- [ ] No unresolved high-severity findings remain.
- [ ] Final commit SHA and test results are recorded in the PR.
