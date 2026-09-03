from __future__ import annotations

from dataclasses import asdict, dataclass
from math import sqrt

import numpy as np
from numpy.typing import NDArray

from .calibration import DarkCalibration


@dataclass(frozen=True)
class DetectionConfig:
    seed_z: float = 8.0
    grow_z: float = 5.0
    component_z: float = 12.0
    min_pixels: int = 2

    def __post_init__(self) -> None:
        if self.grow_z >= self.seed_z:
            raise ValueError("grow_z must be lower than seed_z")
        if self.min_pixels < 1:
            raise ValueError("min_pixels must be positive")


@dataclass(frozen=True)
class Candidate:
    label: str
    area_pixels: int
    centroid_x: float
    centroid_y: float
    peak_z: float
    aggregate_z: float
    integrated_excess_dn: float
    length_pixels: float
    width_pixels: float
    eccentricity: float
    saturated: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _neighbors(y: int, x: int, height: int, width: int):
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            ny, nx = y + dy, x + dx
            if 0 <= ny < height and 0 <= nx < width:
                yield ny, nx


def _components(mask: NDArray[np.bool_]) -> list[list[tuple[int, int]]]:
    height, width = mask.shape
    seen = np.zeros_like(mask)
    result: list[list[tuple[int, int]]] = []
    for y, x in np.argwhere(mask):
        if seen[y, x]:
            continue
        stack = [(int(y), int(x))]
        seen[y, x] = True
        component: list[tuple[int, int]] = []
        while stack:
            cy, cx = stack.pop()
            component.append((cy, cx))
            for ny, nx in _neighbors(cy, cx, height, width):
                if mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    stack.append((ny, nx))
        result.append(component)
    return result


def _shape(
    points: NDArray[np.float64], weights: NDArray[np.float64]
) -> tuple[float, float, float]:
    if len(points) == 1:
        return 1.0, 1.0, 0.0
    centered = points - np.average(points, axis=0, weights=weights)
    covariance = (centered * weights[:, None]).T @ centered / weights.sum()
    eigenvalues = np.maximum(np.linalg.eigvalsh(covariance), 0.0)
    width, length = 2.0 * np.sqrt(eigenvalues + 0.25)
    eccentricity = sqrt(max(0.0, 1.0 - (width * width) / (length * length)))
    return float(length), float(width), eccentricity


def _morphology(area: int, length: float, width: float) -> str:
    aspect = length / max(width, 1e-9)
    if area <= 2:
        return "pointlike"
    if aspect >= 3.0 and length >= 3.0:
        return "linear"
    if aspect >= 1.6:
        return "elongated"
    return "diffuse"


def detect_candidates(
    frame: NDArray[np.generic],
    calibration: DarkCalibration,
    config: DetectionConfig = DetectionConfig(),
) -> list[Candidate]:
    image = np.asarray(frame, dtype=np.float64)
    if image.ndim != 2 or image.shape != calibration.background.shape:
        raise ValueError("frame shape does not match calibration")
    if not np.all(np.isfinite(image)):
        raise ValueError("frame contains non-finite values")

    excess = image - calibration.background
    z = excess / calibration.noise
    z[calibration.bad_pixels] = -np.inf
    seeds = z >= config.seed_z
    growth = z >= config.grow_z
    saturation_value = np.iinfo(frame.dtype).max if np.issubdtype(frame.dtype, np.integer) else None

    candidates: list[Candidate] = []
    for component in _components(growth):
        ys = np.fromiter((p[0] for p in component), dtype=np.int64)
        xs = np.fromiter((p[1] for p in component), dtype=np.int64)
        if len(component) < config.min_pixels or not np.any(seeds[ys, xs]):
            continue

        component_excess = excess[ys, xs]
        component_noise = calibration.noise[ys, xs]
        aggregate_z = float(component_excess.sum() / np.sqrt(np.square(component_noise).sum()))
        if aggregate_z < config.component_z:
            continue

        weights = np.maximum(component_excess, 0.0) + np.finfo(np.float64).eps
        points = np.column_stack((xs, ys)).astype(np.float64)
        centroid_x, centroid_y = np.average(points, axis=0, weights=weights)
        length, width, eccentricity = _shape(points, weights)
        saturated = bool(
            saturation_value is not None and np.any(image[ys, xs] >= saturation_value)
        )
        candidates.append(
            Candidate(
                label=_morphology(len(component), length, width),
                area_pixels=len(component),
                centroid_x=float(centroid_x),
                centroid_y=float(centroid_y),
                peak_z=float(np.max(z[ys, xs])),
                aggregate_z=aggregate_z,
                integrated_excess_dn=float(component_excess.sum()),
                length_pixels=length,
                width_pixels=width,
                eccentricity=eccentricity,
                saturated=saturated,
            )
        )
    return sorted(candidates, key=lambda candidate: candidate.aggregate_z, reverse=True)

