from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
BoolArray = NDArray[np.bool_]


@dataclass(frozen=True)
class DarkCalibration:
    background: FloatArray
    noise: FloatArray
    bad_pixels: BoolArray
    frame_count: int

    def save(self, path: str) -> None:
        with open(path, "wb") as destination:
            np.savez_compressed(
                destination,
                background=self.background,
                noise=self.noise,
                bad_pixels=self.bad_pixels,
                frame_count=np.int64(self.frame_count),
            )

    @classmethod
    def load(cls, path: str) -> "DarkCalibration":
        with np.load(path) as data:
            return cls(
                background=np.asarray(data["background"], dtype=np.float64),
                noise=np.asarray(data["noise"], dtype=np.float64),
                bad_pixels=np.asarray(data["bad_pixels"], dtype=np.bool_),
                frame_count=int(data["frame_count"]),
            )


def _require_stack(frames: NDArray[np.generic]) -> FloatArray:
    stack = np.asarray(frames, dtype=np.float64)
    if stack.ndim != 3 or stack.shape[0] < 5:
        raise ValueError("dark calibration requires at least five 2-D frames")
    if not np.all(np.isfinite(stack)):
        raise ValueError("dark calibration contains non-finite values")
    return stack


def calibrate_dark(
    frames: NDArray[np.generic],
    *,
    hot_sigma: float = 10.0,
    min_noise: float = 0.5,
) -> DarkCalibration:
    """Estimate per-pixel dark level, robust noise, and persistent defects."""
    stack = _require_stack(frames)
    background = np.median(stack, axis=0)
    absolute_deviation = np.abs(stack - background)
    noise = 1.4826 * np.median(absolute_deviation, axis=0)
    noise = np.maximum(noise, min_noise)

    global_dark = float(np.median(background))
    spatial_mad = 1.4826 * float(np.median(np.abs(background - global_dark)))
    spatial_scale = max(spatial_mad, min_noise)
    persistent_hot = background > global_dark + hot_sigma * spatial_scale

    excursions = stack > background + 8.0 * noise
    recurrent = np.mean(excursions, axis=0) > 0.05
    bad_pixels = persistent_hot | recurrent
    return DarkCalibration(background, noise, bad_pixels, stack.shape[0])


def standardized_frames(
    frames: NDArray[np.generic], calibration: DarkCalibration
) -> FloatArray:
    stack = np.asarray(frames, dtype=np.float64)
    if stack.ndim != 3 or stack.shape[1:] != calibration.background.shape:
        raise ValueError("frame stack shape does not match calibration")
    return (stack - calibration.background) / calibration.noise


def derive_seed_threshold(
    null_frames: NDArray[np.generic],
    calibration: DarkCalibration,
    *,
    quantile: float = 0.999,
    floor: float = 8.0,
) -> float:
    """Derive a family-wise threshold from held-out per-frame maxima."""
    if not 0.5 < quantile < 1.0:
        raise ValueError("quantile must be between 0.5 and 1")
    z = standardized_frames(null_frames, calibration)
    z[:, calibration.bad_pixels] = -np.inf
    maxima = np.max(z, axis=(1, 2))
    return max(floor, float(np.quantile(maxima, quantile)))
