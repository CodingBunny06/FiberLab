# De Broglie Matter-Wave Experiment

## Aim
To visualize the wave nature of matter using the De Broglie hypothesis and study how the associated wavelength varies with particle momentum.

## Theory
Louis de Broglie's hypothesis associates a wavelength with a particle having momentum:

\[
\lambda = \frac{h}{p}
\]

For a non-relativistic particle, momentum is \(p=mv\), therefore:

\[
\lambda = \frac{h}{mv}
\]

where \(h=6.62607015\times10^{-34}\,\mathrm{J\,s}\), \(m\) is particle mass in kg and \(v\) is particle speed in m/s.

## Application workflow
1. Select an electron, proton, neutron or custom particle.
2. Set its mass (custom particle only) and speed.
3. The application calculates momentum and De Broglie wavelength.
4. A normalized sinusoidal curve illustrates spatial periodicity over four wavelengths.
5. A log-log graph shows how wavelength changes with speed for the selected mass.

## Assumptions and interpretation
- The calculator uses the non-relativistic relation \(p=mv\).
- Speeds must be below the speed of light. The application displays a caution above 0.1c; a relativistic momentum model is not included in this version.
- The plotted sinusoid is a conceptual visualization of wavelength. It is not a literal path followed by a particle, nor a full solution of the Schrödinger equation.
- The wave amplitude control changes only the normalized display scale; it does not change the calculated wavelength.

## Expected observation
For a fixed particle mass, increasing speed increases momentum and decreases the De Broglie wavelength. More massive particles at the same speed also have shorter wavelengths.
