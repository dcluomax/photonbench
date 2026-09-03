from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def hadamard_patterns(side: int) -> NDArray[np.int8]:
    """Return a complete signed Hadamard basis for a side-by-side image."""
    pixels = side * side
    if side < 1 or pixels & (pixels - 1):
        raise ValueError("side squared must be a positive power of two")
    matrix = np.array([[1]], dtype=np.int8)
    while matrix.shape[0] < pixels:
        matrix = np.block([[matrix, matrix], [matrix, -matrix]])
    return matrix.reshape(pixels, side, side)


def complementary_exposures(
    signed_patterns: NDArray[np.generic],
) -> tuple[NDArray[np.uint8], NDArray[np.uint8]]:
    patterns = np.asarray(signed_patterns)
    if patterns.ndim != 3 or not np.all(np.isin(patterns, (-1, 1))):
        raise ValueError("signed patterns must contain only -1 and 1")
    positive = (patterns > 0).astype(np.uint8)
    return positive, 1 - positive


def reconstruct_differential(
    signed_patterns: NDArray[np.generic],
    positive_buckets: NDArray[np.generic],
    negative_buckets: NDArray[np.generic],
) -> NDArray[np.float64]:
    """Reconstruct from complementary bucket differences."""
    patterns = np.asarray(signed_patterns, dtype=np.float64)
    positive = np.asarray(positive_buckets, dtype=np.float64)
    negative = np.asarray(negative_buckets, dtype=np.float64)
    expected = (patterns.shape[0],) if patterns.ndim == 3 else ()
    if patterns.ndim != 3 or positive.shape != expected or negative.shape != expected:
        raise ValueError("each signed pattern requires positive and negative buckets")
    differential = positive - negative
    return np.tensordot(differential, patterns, axes=(0, 0)) / patterns.shape[0]


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


def contrast_to_noise(
    reconstruction: NDArray[np.generic],
    object_mask: NDArray[np.generic],
) -> float:
    image = np.asarray(reconstruction, dtype=np.float64)
    mask = np.asarray(object_mask, dtype=np.bool_)
    if image.shape != mask.shape or not np.any(mask) or np.all(mask):
        raise ValueError("mask must select a nonempty subset of the image")
    signal = image[mask]
    background = image[~mask]
    denominator = np.sqrt((signal.var() + background.var()) / 2.0)
    if denominator == 0:
        return float("inf") if signal.mean() != background.mean() else 0.0
    return float((signal.mean() - background.mean()) / denominator)


def permutation_p_value(
    signed_patterns: NDArray[np.generic],
    positive_buckets: NDArray[np.generic],
    negative_buckets: NDArray[np.generic],
    truth: NDArray[np.generic],
    *,
    permutations: int = 999,
    seed: int = 0,
) -> float:
    """One-sided p-value for reconstruction correlation under wrong associations."""
    if permutations < 1:
        raise ValueError("permutations must be positive")
    patterns = np.asarray(signed_patterns)
    positive = np.asarray(positive_buckets)
    negative = np.asarray(negative_buckets)
    observed = normalized_correlation(
        reconstruct_differential(patterns, positive, negative), truth
    )
    rng = np.random.default_rng(seed)
    exceedances = 0
    for _ in range(permutations):
        order = rng.permutation(patterns.shape[0])
        shuffled = reconstruct_differential(patterns, positive[order], negative[order])
        if normalized_correlation(shuffled, truth) >= observed:
            exceedances += 1
    return (exceedances + 1.0) / (permutations + 1.0)
