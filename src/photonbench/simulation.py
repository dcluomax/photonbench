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

