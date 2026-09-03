# Garage projects

PhotonBench garage builds are ordered by how quickly they produce a compelling,
reproducible result without weakening the evidence boundary.

| Order | Build | Typical incremental cost | Result |
|---|---|---:|---|
| 1 | [GhostBox-32](ghostbox-32/README.md) | $0–20 | Classical image reconstructed from scalar bucket readings |
| 2 | DarkBox Zero | $0–20 | Long-run particle-like transient candidate survey |
| 3 | PiRAW Metrology | $50–100 | Conversion gain, read noise, linearity, dark current |
| 4 | SPAD-ToF Range/Multipath | $20–120 | Processed range or aggregate timing histograms |
| 5 | Coincidence Ladder | $100+ | Excess coincident penetrating-event candidates |
| 6 | HBT | Laboratory equipment | Nonclassical statistics only if a witness passes |

## Selection logic

GhostBox is first because it is deterministic, visual, safe, and exercises the
same acquisition, synchronization, manifest, and control infrastructure needed
by later builds. DarkBox is second because rare-event attribution takes days of
data and a large held-out null set. SPAD-ToF modules are useful computational
imaging instruments, but their aggregate histograms or processed ranges are not
individual photon time tags and cannot support `g2` claims.

The repository deliberately excludes instructions for harvested radioactive
sources, modified laser projectors, SPDC construction, or other hazardous
shortcuts.

