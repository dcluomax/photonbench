# GhostBox-32

GhostBox-32 reconstructs a 32×32 target from scalar brightness measurements.
The camera is deliberately reduced to a **bucket detector**: every captured
frame contributes one number. The image emerges by correlating those numbers
with known illumination patterns.

This is **physical classical computational ghost imaging**, also called
single-pixel structured-light imaging. It is not quantum ghost imaging.

## Why it is a good garage build

- Uses an existing monitor or intact LED projector and an old webcam.
- Produces a recognizable, visual result in one session.
- Has known ground truth and strong null controls.
- Develops the synchronized acquisition layer later needed by DarkBox.
- Requires no laser, radioactive source, or special optics.

## Bill of materials

| Item | Purpose |
|---|---|
| Monitor or intact LED projector | Displays binary patterns |
| USB webcam or old camera | Camera-summed bucket detector |
| Cardboard/foam-board tunnel | Rejects ambient light |
| Tracing-paper diffuser | Removes spatial detail at the detector |
| Printed transparency or cut-paper target | 32×32 ground truth |
| Black tape and non-reflective liner | Controls stray light |

Do not open or modify a laser projector. Do not enclose a hot projector or its
power supply in an unventilated combustible box. Flashing patterns may affect
photosensitive viewers; enclose the optical path and avoid looking at it.

## Optical layout

```text
monitor/projector -> target -> diffuser/integrator -> defocused webcam
```

The complete blur footprint must remain inside a fixed ROI. Lock exposure,
gain, white balance, focus, and frame rate. Avoid saturation. Preserve every
full frame for audit even though analysis reduces it to one scalar.

Before the real run, display the target under uniform illumination. If a bucket
frame still resolves the target, add diffusion or defocus. The reconstruction
is still mathematically valid without this step, but it must then be described
as **camera-summed structured imaging**, not a non-imaging bucket experiment.

## Commission the software

```powershell
photonbench ghost-demo --side 16 --output reports\ghostbox-16
photonbench ghost-demo --side 32 --output reports\ghostbox-32
```

The first command uses 256 signed Hadamard modes and 512 simulated physical
exposures. The full 32×32 build uses 1,024 modes and **2,048 exposures**:
one binary pattern and its complement for each signed mode.
The commissioning command requires at least 99 permutations because fewer
cannot reach its `p <= 0.01` acceptance gate; physical runs should use the
default 999 or more.

## Physical protocol

1. Warm the display and camera for 20 minutes.
2. Fix all camera controls and verify their read-back values.
3. Define a bucket ROI containing the entire blurred return.
4. Measure dark and uniform frames.
5. Randomize the order of the 1,024 signed modes.
6. For each mode, display its positive pattern, wait for the display transition,
   capture a valid bucket frame, then repeat for the complement.
7. Retry dropped, clipped, saturated, or transition-contaminated pairs.
8. Repeat the complete run with three independent order seeds.
9. Run every null control below without changing analysis parameters.

The pattern at the target plane may differ from the displayed bitmap due to
projector blur, keystone correction, gamma, and flare. Photograph or otherwise
calibrate delivered patterns at the object plane for quantitative work.
Complementary pairs suppress slow common changes but do not make drift vanish:
a fixed change between each positive and negative exposure can project into a
Hadamard-basis artifact while leaving NCC deceptively high. Preserve uniform
controls, inspect residual images, randomize mode order, and require replication.

## Required controls

- **Wrong association:** randomly permute buckets relative to patterns.
- **Timing offset:** pair each bucket with the preceding/following pattern.
- **Blocked path:** block light after the target.
- **Uniform target:** remove spatial target structure.
- **Pattern-free:** hold uniform illumination at the same average brightness.
- **Replication:** use three independently randomized pattern orders.
- **Direct comparator:** capture a direct image at equal total exposure time.

Do not claim equal photon dose unless illumination is radiometrically calibrated.

## Acceptance gates

For each of three physical runs:

- every pattern and complement has exactly one valid bucket measurement;
- no ROI clipping or saturated measurements;
- normalized correlation (`NCC`) at least 0.5;
- contrast-to-noise ratio (`CNR`) at least 5;
- one-sided permutation `p <= 0.01` using at least 999 permutations; and
- blocked, pattern-free, offset, and wrong-association controls fail the same
  reconstruction gate, with offset/wrong-association `NCC < 0.2`.

These are engineering acceptance thresholds, not quantum criteria.

## Planned live adapter

The next implementation adds:

```text
photonbench doctor --adapter uvc
photonbench ghost capture projects/ghostbox-32/protocol.json
photonbench ghost analyze runs/<run-id>
photonbench verify runs/<run-id>
```

Each run will preserve the native frames, bucket values, pattern IDs, retries,
control readbacks, timestamps, temperature, Git commit, random seed, checksums,
and deterministic JSON report.
