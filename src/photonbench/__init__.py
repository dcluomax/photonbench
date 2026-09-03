"""Evidence-gated CMOS and photon-detection experiments."""

from .calibration import DarkCalibration, calibrate_dark, derive_seed_threshold
from .detection import Candidate, DetectionConfig, detect_candidates

__all__ = [
    "Candidate",
    "DarkCalibration",
    "DetectionConfig",
    "calibrate_dark",
    "derive_seed_threshold",
    "detect_candidates",
]

