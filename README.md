# PhotonBench

PhotonBench is an evidence-gated, open-source laboratory for exploring what old
webcams, Raspberry Pi cameras, linear RAW CMOS sensors, and later SPAD hardware
can actually detect.

The first release focuses on:

- calibrating a covered sensor from dark frames;
- detecting statistically significant, particle-like transient candidates;
- extracting morphology without claiming particle species;
- simulating controlled events and measuring recovery;
- reconstructing **classical** computational ghost images; and
- preventing results from being labeled quantum without an appropriate
  nonclassicality witness.

## Scientific boundary

| Evidence | Allowed wording | Not established |
|---|---|---|
| Processed webcam frames | extreme-low-light or empirical transient detection | electrons, photons, quantum behavior |
| Verified linear RAW CMOS | sensor noise and calibrated collected charge | individual visible photons |
| Covered CMOS transient | particle-like transient candidate | cosmic origin, species, direction, energy |
| Known patterns + bucket readings | classical computational ghost imaging | quantum ghost imaging |
| SPAD clicks | single-photon-sensitive detection | nonclassical light |
| Two-detector correlation with confidence bounds | measured `g2` behavior | entanglement without a separate witness |

A commodity CMOS pixel can absorb one visible photon, but its read noise, dark
current, ADC, image-processing pipeline, and compression normally prevent that
one photon from being identified. Low illumination is not a quantum witness.

## Quick start

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\photonbench demo --output reports\demo
.\.venv\Scripts\pytest
```

The demo creates a synthetic dark calibration set, injects a line-shaped event,
derives an empirical threshold from held-out null frames, and writes a JSON
candidate report. It proves software behavior only; it does not validate a
physical detector.

To analyze NumPy arrays captured elsewhere:

```powershell
photonbench calibrate-dark data\calibration.npy reports\dark-model.npz
photonbench detect data\frame.npy reports\dark-model.npz reports\events.json
```

`calibration.npy` has shape `(frames, rows, columns)`. Analysis inputs must be
native, lossless arrays. JPEG screenshots are never scientific inputs.

## Detection model

For pixel `i` in frame `t`, PhotonBench computes:

```text
z(i,t) = (frame(i,t) - dark_median(i)) / dark_sigma(i)
```

The robust per-pixel sigma comes from median absolute deviation. A seed pixel
must exceed the independently calibrated seed threshold; its region grows only
through pixels above a lower threshold. Connected components are then filtered
by aggregate significance and known defective pixels.

The fixed defaults are bootstrap values. For real claims, use a later,
temperature-matched null run and derive the seed threshold from the distribution
of each frame's maximum z-score. Zero false detections in `M` independent null
frames gives only an approximate 95% upper false-event rate of `3/M`.

## Recommended project path

1. **Sensor audit:** determine native pixel format and whether response is
   linear with exposure. Record requested and read-back controls.
2. **Dark calibration:** capture warm, light-tight dark frames at matched
   exposure, gain, resolution, and temperature.
3. **Frozen detection:** derive thresholds on calibration data, then stop
   tuning before evaluating held-out data.
4. **Injection validation:** inject point, line, and curved signals into real
   held-out dark frames; report recall versus signal and empirical false alarms.
5. **Physical validation:** use independent sensors or a characterized
   scintillator detector and compare zero-lag coincidences with time shifts.
6. **Classical imaging:** run complementary structured patterns and shuffled,
   blocked-path, and synchronization-offset null controls.
7. **SPAD extension:** add a capability-specific adapter only after measuring
   dark counts, dead time, afterpulsing, crosstalk, and timing jitter.

See [the detection protocol](docs/detection-protocol.md),
[hardware guide](docs/hardware.md), and [research notes](docs/research.md).

## Safety

No radioactive source or laser is required. Do not dismantle smoke detectors or
build from loose radioactive material. Any source must be lawful, sealed,
documented, and handled under applicable radiation-safety rules.

Do not attempt an SPDC/entanglement optical setup from this repository. Such
setups commonly involve Class 3B violet/UV pump lasers and require trained
supervision, wavelength-rated protection, enclosed beam paths, beam dumps, and
real hardware interlocks. A software checkbox is not a safety interlock.

