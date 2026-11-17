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
4. Set the physical plot window in nanometres. The horizontal axis represents this actual distance, rather than a wavelength-normalized coordinate.
5. Observe how the number of visible oscillations changes as the selected particle, speed or plot window changes.
6. Compare electron, proton and neutron wavelengths at the selected speed using the logarithmic comparison chart.
7. A log-log graph shows how wavelength changes with speed for the selected mass.

## Assumptions and interpretation
- The calculator uses the non-relativistic relation \(p=mv\).
- Speeds must be below the speed of light. The application displays a caution above 0.1c; a relativistic momentum model is not included in this version.
- The plotted sinusoid is a conceptual visualization of spatial periodicity. It is not a literal path followed by a particle, nor a full solution of the Schrödinger equation.
- The wave amplitude control changes only the display scale; it does not change the calculated wavelength.
- Very short wavelengths can produce too many cycles to render clearly in a finite plot. The application warns when the selected physical window exceeds its rendering limit.

## Expected observation
For a fixed particle mass, increasing speed increases momentum and decreases the De Broglie wavelength. More massive particles at the same speed also have shorter wavelengths. Over the same physical distance, a shorter wavelength produces more oscillations.
