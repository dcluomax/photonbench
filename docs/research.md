# Research notes and roadmap

## What existing work establishes

- Consumer CMOS sensors can record large charge-deposition transients in
  light-tight operation. Existing citizen-science systems demonstrate practical
  acquisition, but thresholding and morphology alone do not identify cosmic
  origin or particle species.
- Camera characterization should follow the substance of EMVA 1288: paired
  frame differences, linearity, dark current, defect maps, and confidence
  intervals. PhotonBench does not claim EMVA certification.
- Computational ghost imaging can use classical structured illumination and a
  bucket detector. Ghost imaging is not inherently quantum.
- Low-cost ToF sensors such as the AMS TMF8820 contain SPAD arrays and may expose
  histograms, but their on-chip processing and interface define what can
  actually be measured.
- Nonclassical light requires a statistical witness, not merely a sensitive
  detector. Examples include an upper confidence bound below one for
  `g2(0)` antibunching, a classical Cauchy-Schwarz violation, or an appropriate
  Bell/entanglement witness.

## Primary anchors

1. EMVA, *EMVA Standard 1288, Release 4.0 Linear*:
   https://www.emva.org/standards-technology/emva-1288/
2. Vandenbroucke et al., *Measurement of cosmic-ray and radioactive particle
   tracks with a cellphone camera*, JINST 11 (2016):
   https://doi.org/10.1088/1748-0221/11/04/P04019
3. Whiteson et al., *Observing ultra-high energy cosmic rays with smartphones*,
   Astroparticle Physics 79 (2016):
   https://doi.org/10.1016/j.astropartphys.2016.02.002
4. Shapiro, *Computational ghost imaging*, Physical Review A 78 (2008):
   https://doi.org/10.1103/PhysRevA.78.061802
5. Erkmen and Shapiro, *Ghost imaging: from quantum to classical to
   computational*, Advances in Optics and Photonics 2 (2010):
   https://doi.org/10.1364/AOP.2.000405
6. Bruschini et al., *Single-photon avalanche diode imagers in biophotonics*,
   Light: Science & Applications 8 (2019):
   https://doi.org/10.1038/s41377-019-0191-5
7. Mu et al., *Towards 3D Vision with Low-Cost Single-Photon Cameras*, CVPR
   2024, including AMS TMF8820 histogram data:
   https://github.com/uwgraphics/LCSPCData
8. SORAMAME public Raspberry Pi acquisition subset:
   https://github.com/soramame-cosmicray/soramame_pi
9. CREDO CMOSmicRay Raspberry Pi implementation:
   https://github.com/credo-science/credo-cmosmicray-raspberry-pi-model-b

## Roadmap

### v0.1 — reproducible offline detector

- dark calibration and defect mask;
- held-out empirical threshold;
- connected-component morphology;
- simulation and injection tests;
- report claim boundary;
- classical covariance reconstruction.

### v0.2 — real acquisition and validation

- Picamera2 RAW and UVC processed-frame adapters;
- immutable run manifest and control readback;
- streaming ring buffer and negative sampling;
- threshold calibration and injection-efficiency reports;
- exposure linearity and paired-frame photon-transfer analysis.

### v0.3 — physical coincidence

- clock model and exposure-interval overlap;
- time-shift accidental estimator;
- dual-sensor and reference-scintillator adapters;
- rate confidence intervals and device-held-out validation.

### v0.4 — structured imaging

- complementary pattern generator and synchronized acquisition;
- differential bucket reconstruction;
- blocked, shuffled, and offset null experiments;
- NCC, CNR, dose, replication, and permutation reports.

### Later — photon-sensitive hardware

- binary/counting/time-tag capability interfaces;
- SPAD/SiPM characterization;
- two-detector `g2` analysis;
- nonclassicality gate with explicit statistical assumptions.

Quantum ghost imaging remains out of scope until the project has a validated
source, coincidence-resolved detectors, accidental subtraction, and a defensible
nonclassical correlation or entanglement witness.

