# Detection protocol

## 1. Audit the sensor before believing it

Record the camera model, sensor if known, firmware, driver, native pixel format,
bit depth, resolution, exposure, analog/digital gain, frame rate, temperature,
sequence number, dropped frames, and monotonic plus UTC timestamps. Record both
requested and read-back controls.

Classify the input:

- `processed-frame`: RGB/YUV/MJPEG or unknown image signal processing;
- `linear-frame`: native Bayer/mono response demonstrated linear with exposure;
- `binary-spad`, `counting-spad`, or `timetag-spad`: only after hardware
  capability and timing behavior are characterized.

YUY2 is not RAW merely because it is uncompressed. Gamma, denoising,
demosaicing, clipping, and temporal processing can invalidate a physical noise
model. OpenCV timestamps are software arrival times, not exposure timestamps.

## 2. Capture calibration data

Warm the sensor for at least 20 minutes. Make the enclosure light-tight. For
each operating resolution, format, gain, exposure, and temperature band:

1. Capture at least 200 dark frames for development.
2. Capture a separate, later null set for threshold selection.
3. Capture a third held-out set for the final false-alarm measurement.
4. Save native arrays and immutable metadata before processing.

Do not optical-flat-field particle data. Color filters and microlenses affect
photons entering through the normal optical path, not charge deposited inside
silicon. Do not debayer candidate frames.

## 3. Calibrate and freeze

PhotonBench estimates each pixel's median dark level and robust temporal noise.
Persistent hot and recurrent pixels form a defect mask. The release threshold
comes from held-out per-frame maximum z-scores, controlling the search across
all pixels more honestly than a fixed per-pixel threshold.

Freeze calibration hashes, thresholds, exclusion masks, and component cuts
before evaluating final data. Never tune on the final run.

## 4. Detect and retain provenance

The detector uses:

1. high-significance seed pixels;
2. lower-significance eight-connected region growth;
3. aggregate component significance;
4. defect masking; and
5. morphology-only labels.

Store candidate crops plus neighboring frames, and retain a reservoir sample of
negative frames. Store per-frame maxima and cut-flow counts even when the full
negative stream is too large to preserve.

Labels such as `linear`, `elongated`, `pointlike`, and `diffuse` describe pixel
shape only. They do not prove muons, beta particles, gamma rays, direction, or
energy. Saturated candidate intensity is a lower bound.

## 5. Validate detection

### Software validation

Inject synthetic point, line, curved, and diffuse charge patterns into held-out
real dark frames. Sweep position, angle, length, and signal. Report:

- detection probability versus injected signal;
- localization and morphology error;
- false detections per frame and per live hour;
- temperature dependence; and
- all rejection cut counts.

If no false candidates occur in `M` independent null frames, the approximate
95% upper false-event probability is `3/M`. A bound of one per million frames
therefore requires roughly three million valid null frames.

### Physical validation

A single covered camera supports only “particle-like transient candidate.”
Stronger attribution requires independent coincidence:

- two aligned sensors with measured exposure intervals; or
- preferably, a characterized scintillator plus SiPM/reference detector.

Compare zero-lag coincidences with many positive and negative timestamp shifts.
The excess is `N(0) - mean(N(shifted))`; report a Poisson or permutation
confidence interval and live-time normalization. Rolling shutter, clock drift,
and timestamp jitter must be included in the coincidence window.

## 6. Null controls

Run interleaved controls for:

- light leaks and enclosure movement;
- temperature drift;
- recurring hot/random-telegraph pixels;
- row/column readout faults;
- JPEG/codec block alignment;
- USB corruption, duplicates, and dropped frames;
- power-supply or EMI transients; and
- shuffled or time-shifted coincidence streams.

An attractive image is not validation. Raw measurements, null experiments,
uncertainty, and replication are the result.

