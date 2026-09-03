from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .calibration import DarkCalibration, calibrate_dark, derive_seed_threshold
from .detection import DetectionConfig, detect_candidates
from .ghost import (
    complementary_exposures,
    contrast_to_noise,
    hadamard_patterns,
    normalized_correlation,
    permutation_p_value,
    reconstruct_differential,
)
from .simulation import (
    inject_line,
    simulate_complementary_buckets,
    simulate_dark_frames,
)


def _ghost_side(value: str) -> int:
    side = int(value)
    pixels = side * side
    if side < 4 or pixels & (pixels - 1):
        raise argparse.ArgumentTypeError(
            "side must be at least 4 and side squared must be a power of two"
        )
    return side


def _permutation_count(value: str) -> int:
    count = int(value)
    if count < 99:
        raise argparse.ArgumentTypeError(
            "at least 99 permutations are required for the p <= 0.01 gate"
        )
    return count


def _write_report(path: Path, candidates, *, seed_z: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "claim": "particle-like transient candidate",
        "seed_z": seed_z,
        "candidate_count": len(candidates),
        "candidates": [candidate.to_dict() for candidate in candidates],
        "limitations": [
            "Morphology does not identify particle species or cosmic origin.",
            "Integrated DN is not deposited particle energy.",
        ],
    }
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def _demo(output: Path) -> int:
    output.mkdir(parents=True, exist_ok=True)
    calibration_frames = simulate_dark_frames(256, (64, 64), seed=10)
    null_frames = simulate_dark_frames(512, (64, 64), seed=11)
    calibration = calibrate_dark(calibration_frames)
    seed_z = derive_seed_threshold(null_frames, calibration, quantile=0.999)
    test_frame = inject_line(
        simulate_dark_frames(1, (64, 64), seed=12)[0],
        start=(15, 9),
        end=(42, 36),
        signal=30.0,
    )
    candidates = detect_candidates(
        test_frame,
        calibration,
        DetectionConfig(seed_z=seed_z),
    )
    calibration.save(str(output / "dark-model.npz"))
    np.save(output / "synthetic-event.npy", test_frame)
    _write_report(output / "events.json", candidates, seed_z=seed_z)
    print(f"Detected {len(candidates)} candidate(s); report: {output / 'events.json'}")
    return 0 if candidates else 1


def _ghost_demo(output: Path, side: int, permutations: int) -> int:
    output.mkdir(parents=True, exist_ok=True)
    truth = np.zeros((side, side), dtype=np.float64)
    margin = max(1, side // 4)
    truth[margin:-margin, side // 2 - 1 : side // 2 + 1] = 1.0
    truth[margin : margin + 2, margin:-margin] = 1.0
    patterns = hadamard_patterns(side)
    positive_patterns, negative_patterns = complementary_exposures(patterns)
    positive, negative = simulate_complementary_buckets(
        patterns,
        truth,
        noise_sigma=max(0.25, side / 32),
        drift_per_exposure=0.001,
        seed=21,
    )
    reconstruction = reconstruct_differential(patterns, positive, negative)
    ncc = normalized_correlation(reconstruction, truth)
    cnr = contrast_to_noise(reconstruction, truth > 0)
    p_value = permutation_p_value(
        patterns,
        positive,
        negative,
        truth,
        permutations=permutations,
        seed=22,
    )
    offset_reconstruction = reconstruct_differential(
        patterns, np.roll(positive, 1), np.roll(negative, 1)
    )
    offset_ncc = normalized_correlation(offset_reconstruction, truth)
    passed = ncc >= 0.5 and cnr >= 5.0 and p_value <= 0.01 and offset_ncc < 0.2
    np.savez_compressed(
        output / "ghostbox-demo.npz",
        truth=truth,
        positive_patterns=positive_patterns,
        negative_patterns=negative_patterns,
        positive_buckets=positive,
        negative_buckets=negative,
        reconstruction=reconstruction,
        offset_reconstruction=offset_reconstruction,
    )
    report = {
        "claim": "classical computational ghost imaging simulation",
        "side": side,
        "signed_modes": int(patterns.shape[0]),
        "physical_exposures": int(patterns.shape[0] * 2),
        "ncc": ncc,
        "cnr": cnr,
        "permutation_p_value": p_value,
        "offset_control_ncc": offset_ncc,
        "passed": passed,
        "limitations": [
            "This hardware-free simulation validates software, not a physical setup.",
            "Structured-light correlation is classical and does not establish quantum behavior.",
        ],
    }
    report_path = output / "report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"GhostBox {'passed' if passed else 'failed'}; report: {report_path}")
    return 0 if passed else 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="photonbench")
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo", help="run a hardware-free detection demo")
    demo.add_argument("--output", type=Path, default=Path("reports/demo"))

    ghost_demo = commands.add_parser(
        "ghost-demo", help="commission GhostBox reconstruction without hardware"
    )
    ghost_demo.add_argument("--output", type=Path, default=Path("reports/ghost-demo"))
    ghost_demo.add_argument("--side", type=_ghost_side, default=16)
    ghost_demo.add_argument("--permutations", type=_permutation_count, default=999)

    calibrate = commands.add_parser("calibrate-dark", help="build a dark model from .npy")
    calibrate.add_argument("frames", type=Path)
    calibrate.add_argument("output", type=Path)

    detect = commands.add_parser("detect", help="detect candidates in a 2-D .npy frame")
    detect.add_argument("frame", type=Path)
    detect.add_argument("calibration", type=Path)
    detect.add_argument("output", type=Path)
    detect.add_argument("--seed-z", type=float, default=8.0)
    detect.add_argument("--grow-z", type=float, default=5.0)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "demo":
        return _demo(args.output)
    if args.command == "ghost-demo":
        return _ghost_demo(args.output, args.side, args.permutations)
    if args.command == "calibrate-dark":
        model = calibrate_dark(np.load(args.frames))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        model.save(str(args.output))
        print(f"Saved dark model from {model.frame_count} frames to {args.output}")
        return 0
    if args.command == "detect":
        model = DarkCalibration.load(str(args.calibration))
        config = DetectionConfig(seed_z=args.seed_z, grow_z=args.grow_z)
        candidates = detect_candidates(np.load(args.frame), model, config)
        _write_report(args.output, candidates, seed_z=args.seed_z)
        print(f"Detected {len(candidates)} candidate(s); report: {args.output}")
        return 0
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
