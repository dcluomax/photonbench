from __future__ import annotations

from enum import Enum


class Capability(str, Enum):
    PROCESSED_FRAME = "processed-frame"
    LINEAR_FRAME = "linear-frame"
    BINARY_SPAD = "binary-spad"
    COUNTING_SPAD = "counting-spad"
    TIMETAG_SPAD = "timetag-spad"


_ALLOWED_CLAIMS = {
    Capability.PROCESSED_FRAME: frozenset({"extreme-low-light", "transient-candidate"}),
    Capability.LINEAR_FRAME: frozenset(
        {"extreme-low-light", "transient-candidate", "collected-electron-statistics"}
    ),
    Capability.BINARY_SPAD: frozenset({"single-photon-sensitive-clicks"}),
    Capability.COUNTING_SPAD: frozenset(
        {"single-photon-sensitive-clicks", "photon-counting-statistics"}
    ),
    Capability.TIMETAG_SPAD: frozenset(
        {"single-photon-sensitive-clicks", "photon-counting-statistics", "g2-correlation"}
    ),
}


def require_claim(capability: Capability, claim: str) -> None:
    if claim not in _ALLOWED_CLAIMS[capability]:
        raise ValueError(f"{capability.value} evidence cannot support claim {claim!r}")


def require_nonclassical_witness(
    *,
    witness: str,
    estimate: float,
    upper_confidence_bound: float,
) -> None:
    if witness != "g2-antibunching":
        raise ValueError("unsupported nonclassicality witness")
    if not (0.0 <= estimate <= upper_confidence_bound < 1.0):
        raise ValueError("g2 nonclassical claim requires an upper confidence bound below 1")

