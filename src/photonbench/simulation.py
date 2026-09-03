from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def simulate_dark_frames(
    count: int,
    shape: tuple[int, int],
    *,
    bias: float = 100.0,
    read_noise: float = 2.0,
    seed: int = 0,
) -> NDArray[np.float64]:
    if count < 1 or min(shape) < 1 or read_noise <= 0:
        raise ValueError("invalid simulation dimensions or noise")
    rng = np.random.default_rng(seed)
    fixed_pattern = rng.normal(0.0, 0.25, size=shape)
    return bias + fixed_pattern + rng.normal(0.0, read_noise, size=(count, *shape))


def inject_line(
    frame: NDArray[np.generic],
    *,
    start: tuple[int, int],
    end: tuple[int, int],
    signal: float,
) -> NDArray[np.float64]:
    result = np.asarray(frame, dtype=np.float64).copy()
    y0, x0 = start
    y1, x1 = end
    steps = max(abs(y1 - y0), abs(x1 - x0)) + 1
    ys = np.rint(np.linspace(y0, y1, steps)).astype(int)
    xs = np.rint(np.linspace(x0, x1, steps)).astype(int)
    if np.any(ys < 0) or np.any(ys >= result.shape[0]) or np.any(xs < 0) or np.any(xs >= result.shape[1]):
        raise ValueError("line lies outside frame")
    result[ys, xs] += signal
    return result


def simulate_complementary_buckets(
    signed_patterns: NDArray[np.generic],
    target: NDArray[np.generic],
    *,
    noise_sigma: float = 0.5,
    drift_per_exposure: float = 0.0,
    seed: int = 0,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Simulate positive/negative camera-summed bucket measurements."""
    patterns = np.asarray(signed_patterns)
    image = np.asarray(target, dtype=np.float64)
    if patterns.ndim != 3 or patterns.shape[1:] != image.shape:
        raise ValueError("pattern and target shapes do not match")
    if noise_sigma < 0:
        raise ValueError("noise_sigma cannot be negative")
    positive = (patterns > 0).astype(np.float64)
    negative = 1.0 - positive
    rng = np.random.default_rng(seed)
    index = np.arange(patterns.shape[0], dtype=np.float64)
    positive_buckets = np.sum(positive * image, axis=(1, 2))
    negative_buckets = np.sum(negative * image, axis=(1, 2))
    positive_buckets += (
        drift_per_exposure * (2.0 * index)
        + rng.normal(0.0, noise_sigma, len(index))
    )
    negative_buckets += (
        drift_per_exposure * (2.0 * index + 1.0)
        + rng.normal(0.0, noise_sigma, len(index))
    )
    return positive_buckets, negative_buckets
