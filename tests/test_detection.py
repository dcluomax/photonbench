import numpy as np

from photonbench.calibration import DarkCalibration, calibrate_dark, derive_seed_threshold
from photonbench.detection import DetectionConfig, detect_candidates
from photonbench.simulation import inject_line, simulate_dark_frames


def test_detects_injected_line() -> None:
    calibration = calibrate_dark(simulate_dark_frames(200, (32, 32), seed=1))
    frame = simulate_dark_frames(1, (32, 32), seed=2)[0]
    frame = inject_line(frame, start=(5, 4), end=(20, 19), signal=30)

    candidates = detect_candidates(frame, calibration)

    assert len(candidates) == 1
    assert candidates[0].label == "linear"
    assert candidates[0].area_pixels >= 14
    assert candidates[0].aggregate_z > 12


def test_bad_pixel_is_suppressed() -> None:
    frames = simulate_dark_frames(200, (16, 16), seed=3)
    frames[:, 8, 8] += 100
    calibration = calibrate_dark(frames)
    frame = simulate_dark_frames(1, (16, 16), seed=4)[0]
    frame[8, 8] += 200

    assert calibration.bad_pixels[8, 8]
    assert detect_candidates(frame, calibration, DetectionConfig(min_pixels=1)) == []


def test_empirical_threshold_uses_per_frame_maxima() -> None:
    calibration = DarkCalibration(
        background=np.zeros((2, 2)),
        noise=np.ones((2, 2)),
        bad_pixels=np.zeros((2, 2), dtype=bool),
        frame_count=100,
    )
    null = np.zeros((4, 2, 2))
    null[:, 0, 0] = [1.0, 2.0, 10.0, 20.0]

    threshold = derive_seed_threshold(null, calibration, quantile=0.75, floor=0.0)

    assert threshold == 12.5


def test_calibration_save_uses_exact_path(tmp_path) -> None:
    calibration = calibrate_dark(simulate_dark_frames(20, (8, 8), seed=5))
    path = tmp_path / "model-without-extension"

    calibration.save(str(path))
    loaded = DarkCalibration.load(str(path))

    assert path.exists()
    np.testing.assert_array_equal(loaded.background, calibration.background)


def test_shape_mismatch_fails() -> None:
    calibration = calibrate_dark(simulate_dark_frames(20, (8, 8), seed=7))
    with np.testing.assert_raises(ValueError):
        detect_candidates(np.zeros((7, 8)), calibration)
