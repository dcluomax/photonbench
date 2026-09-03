import numpy as np

from photonbench.ghost import normalized_correlation, reconstruct_covariance


def test_classical_ghost_reconstruction_recovers_target() -> None:
    rng = np.random.default_rng(20)
    truth = np.zeros((8, 8))
    truth[2:6, 3:5] = 1
    patterns = rng.integers(0, 2, size=(5000, 8, 8))
    buckets = np.sum(patterns * truth, axis=(1, 2))

    reconstruction = reconstruct_covariance(patterns, buckets)

    assert normalized_correlation(reconstruction, truth) > 0.9

