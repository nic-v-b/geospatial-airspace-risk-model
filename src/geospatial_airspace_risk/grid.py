"""Regular 3D airspace-grid construction and Morton indexing."""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class AirspaceGridSpec:
    """Definition of a regular 3D airspace lattice in Cartesian metres."""

    x_min: float
    y_min: float
    z_min: float
    x_max: float
    y_max: float
    z_max: float
    resolution_m: float

    def validate(self) -> None:
        if self.resolution_m <= 0:
            raise ValueError("resolution_m must be positive.")
        if not (
            self.x_max > self.x_min
            and self.y_max > self.y_min
            and self.z_max > self.z_min
        ):
            raise ValueError("Grid maximum bounds must exceed minimum bounds.")


def _split_by_3bits(value: int) -> int:
    """Spread the low 21 bits so two zero bits separate each source bit."""
    value &= 0x1FFFFF
    value = (value | value << 32) & 0x1F00000000FFFF
    value = (value | value << 16) & 0x1F0000FF0000FF
    value = (value | value << 8) & 0x100F00F00F00F00F
    value = (value | value << 4) & 0x10C30C30C30C30C3
    value = (value | value << 2) & 0x1249249249249249
    return value


def morton3d(ix: int, iy: int, iz: int) -> int:
    """Return a deterministic 3D Morton code for non-negative integer indices."""
    if min(ix, iy, iz) < 0:
        raise ValueError("Morton indices must be non-negative.")
    return (
        _split_by_3bits(ix)
        | (_split_by_3bits(iy) << 1)
        | (_split_by_3bits(iz) << 2)
    )


def _centers(low: float, high: float, resolution: float) -> np.ndarray:
    n = int(np.floor((high - low) / resolution))
    if n <= 0:
        return np.array([], dtype=float)
    return low + (np.arange(n, dtype=float) + 0.5) * resolution


def build_regular_grid(spec: AirspaceGridSpec) -> pd.DataFrame:
    """Build centroid records for the regular 3D grid described by the specification."""
    spec.validate()
    xs = _centers(spec.x_min, spec.x_max, spec.resolution_m)
    ys = _centers(spec.y_min, spec.y_max, spec.resolution_m)
    zs = _centers(spec.z_min, spec.z_max, spec.resolution_m)

    records = []
    centroid_id = 0
    for iz, z in enumerate(zs):
        for iy, y in enumerate(ys):
            for ix, x in enumerate(xs):
                records.append(
                    {
                        "centroid_id": centroid_id,
                        "ix": ix,
                        "iy": iy,
                        "iz": iz,
                        "morton_code": morton3d(ix, iy, iz),
                        "X": float(x),
                        "Y": float(y),
                        "Z": float(z),
                    }
                )
                centroid_id += 1

    return pd.DataFrame.from_records(records)
