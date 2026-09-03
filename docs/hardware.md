# Hardware guide

## Tier 0: any old webcam

Use it first. A UVC webcam with manual exposure and gain can test acquisition,
light sealing, long-run reliability, transient extraction, and classical
structured-light reconstruction. If it only emits processed YUV/MJPEG, results
must remain exploratory and cannot be converted to electrons or photons.

Required:

- opaque, mechanically stable enclosure;
- fixed manual controls where the driver allows them;
- a computer with enough storage for native frames; and
- temperature logging near the camera body.

## Tier 1: RAW-capable CMOS

A Raspberry Pi camera with Picamera2/libcamera RAW output or an astronomy camera
is more useful for sensor metrology. Choose based on documented RAW access,
manual control readback, bit depth, stable long exposures, and lossless capture,
not megapixels.

Before purchasing, verify:

- the exact mode exposes native Bayer/mono values;
- auto exposure, gain, white balance, denoise, sharpening, and compression can
  be disabled;
- actual exposure/gain can be read back;
- long captures do not silently drop into another format; and
- the sensor temperature is measured or an external proxy can be logged.

## Tier 2: classical computational ghost imaging

The lowest-risk setup uses a monitor or projector, a transmissive target, and a
webcam as a deliberately defocused bucket detector. Display known complementary
binary patterns and sum a fixed detector ROI. Confirm an individual bucket frame
does not spatially resolve the target.

Required controls include shuffled bucket order, blocked path, uniform target,
pattern-free illumination, synchronization offsets, at least three pattern
seeds, and a direct-image comparison at equal total exposure.

This is classical computational imaging. It is not quantum ghost imaging.

## Tier 3: SPAD/SiPM research

Treat this as a separate detector and timing project. A low-cost ToF module may
contain SPADs yet expose only processed distance bins; it is not automatically a
general-purpose photon counter. A bare SiPM or SPAD is not a finished instrument.

An adapter must declare whether it supplies binary gates, counts, or time tags.
Characterize dark-count rate, photon-detection efficiency or system efficiency,
dead time, afterpulsing, crosstalk, timing jitter, occupancy, and temperature.
Antibunching requires two independent detectors in an HBT geometry; a
single-detector dead-time dip is not antibunching.

Turnkey detectors and time taggers can dominate cost. Obtain current vendor
quotes and specifications for the chosen experiment rather than relying on a
generic budget.

## Safety exclusions

Ambient background is sufficient for software and long-run studies. This
project does not instruct users to extract radioactive sources from consumer
products. Do not grind, dissolve, open, or modify radioactive material.

The initial release intentionally excludes SPDC construction and Class 3B laser
procedures. Use institutional laser/radiation safety processes for advanced
experiments.

