from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .calibration import DarkCalibration, calibrate_dark, derive_seed_threshold
from .detection import DetectionConfig, detect_candidates
from .simulation import inject_line, simulate_dark_frames


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


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="photonbench")
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo", help="run a hardware-free detection demo")
    demo.add_argument("--output", type=Path, default=Path("reports/demo"))

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

