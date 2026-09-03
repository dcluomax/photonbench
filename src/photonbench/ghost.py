from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def reconstruct_covariance(
    patterns: NDArray[np.generic],
    buckets: NDArray[np.generic],
) -> NDArray[np.float64]:
    """Reconstruct a classical computational ghost image by covariance."""
    p = np.asarray(patterns, dtype=np.float64)
    b = np.asarray(buckets, dtype=np.float64)
    if p.ndim != 3 or b.shape != (p.shape[0],):
        raise ValueError("patterns must be (samples, rows, columns) with one bucket each")
    p_centered = p - p.mean(axis=0)
    b_centered = b - b.mean()
    denominator = np.square(p_centered).sum(axis=0)
    numerator = np.tensordot(b_centered, p_centered, axes=(0, 0))
    return np.divide(
        numerator,
        denominator,
        out=np.zeros_like(numerator),
        where=denominator > 0,
    )


def normalized_correlation(
    reconstruction: NDArray[np.generic],
    truth: NDArray[np.generic],
) -> float:
    a = np.asarray(reconstruction, dtype=np.float64).ravel()
    b = np.asarray(truth, dtype=np.float64).ravel()
    if a.shape != b.shape or np.std(a) == 0 or np.std(b) == 0:
        raise ValueError("inputs must have equal, non-constant shapes")
    return float(np.corrcoef(a, b)[0, 1])

