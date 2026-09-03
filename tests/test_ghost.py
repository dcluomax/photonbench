import numpy as np

from photonbench.ghost import (
    complementary_exposures,
    contrast_to_noise,
    hadamard_patterns,
    normalized_correlation,
    permutation_p_value,
    reconstruct_covariance,
    reconstruct_differential,
)
from photonbench.simulation import simulate_complementary_buckets


def test_classical_ghost_reconstruction_recovers_target() -> None:
    rng = np.random.default_rng(20)
    truth = np.zeros((8, 8))
    truth[2:6, 3:5] = 1
    patterns = rng.integers(0, 2, size=(5000, 8, 8))
    buckets = np.sum(patterns * truth, axis=(1, 2))

    reconstruction = reconstruct_covariance(patterns, buckets)

    assert normalized_correlation(reconstruction, truth) > 0.9


def test_differential_hadamard_reconstruction_and_null() -> None:
    truth = np.zeros((8, 8))
    truth[2:6, 3:5] = 1
    patterns = hadamard_patterns(8)
    positive_images, negative_images = complementary_exposures(patterns)
    positive, negative = simulate_complementary_buckets(
        patterns, truth, noise_sigma=0.05, drift_per_exposure=0.02, seed=30
    )

    reconstruction = reconstruct_differential(patterns, positive, negative)
    shuffled = reconstruct_differential(patterns, positive[::-1], negative[::-1])

    assert positive_images.shape == negative_images.shape == (64, 8, 8)
    assert normalized_correlation(reconstruction, truth) > 0.99
    assert contrast_to_noise(reconstruction, truth > 0) > 10
    assert normalized_correlation(shuffled, truth) < 0.2
    assert (
        permutation_p_value(
            patterns, positive, negative, truth, permutations=99, seed=31
        )
        <= 0.02
    )


def test_sequential_drift_projects_to_known_basis_artifact() -> None:
    truth = np.zeros((8, 8))
    truth[2:6, 3:5] = 1
    patterns = hadamard_patterns(8)
    positive, negative = simulate_complementary_buckets(
        patterns, truth, noise_sigma=0, drift_per_exposure=0.5, seed=32
    )
    reconstruction = reconstruct_differential(patterns, positive, negative)

    expected_artifact = np.zeros_like(truth)
    expected_artifact[0, 0] = -0.5
    np.testing.assert_allclose(reconstruction - truth, expected_artifact, atol=1e-12)
    ncc = normalized_correlation(reconstruction, truth)
    assert 0.95 < ncc < 0.999


def test_hadamard_requires_power_of_two_pixel_count() -> None:
    with np.testing.assert_raises(ValueError):
        hadamard_patterns(3)
