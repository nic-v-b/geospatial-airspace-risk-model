"""Centroid-based convergence and airspace-risk reference calculations."""

from dataclasses import dataclass
from typing import Iterable, Mapping, Optional, Sequence

import numpy as np


@dataclass(frozen=True)
class CollisionRiskResult:
    """Collision-risk result for one centroid and one time step."""

    risk_seconds: Optional[float]
    driving_pair: Optional[tuple[str, str]]
    converging_aircraft: int


def convergence_time(
    current: Sequence[float],
    previous: Sequence[float],
    centroid: Sequence[float],
    delta_t_s: float,
) -> Optional[float]:
    """Estimate time to a centroid when an entity is moving toward it."""
    if delta_t_s <= 0:
        return None

    current_v = np.asarray(current, dtype=float)
    previous_v = np.asarray(previous, dtype=float)
    centroid_v = np.asarray(centroid, dtype=float)

    d_now = float(np.linalg.norm(current_v - centroid_v))
    d_prev = float(np.linalg.norm(previous_v - centroid_v))
    delta_d = d_prev - d_now

    if delta_d <= 0:
        return None

    speed_to_centroid = delta_d / float(delta_t_s)
    if speed_to_centroid <= 0:
        return None

    ct = d_now / speed_to_centroid
    if not np.isfinite(ct) or ct < 0:
        return None
    return float(ct)


def collision_risk_at_centroid(
    aircraft: Iterable[Mapping[str, object]],
    centroid: Sequence[float],
    delta_ct_threshold_s: float,
    max_risk_seconds: Optional[float] = None,
) -> CollisionRiskResult:
    """Calculate the paper-style mid-air collision risk metric at one centroid.

    Aircraft records provide id, current position, previous position, and elapsed
    time. Converging aircraft are ordered by convergence time. Adjacent pairs
    inside the convergence-time threshold are candidate collision-risk pairs.

    For a qualifying ordered pair, the pair risk is min(CT) + delta_CT, which is
    equal to the larger convergence time. The smallest qualifying pair risk drives
    the centroid metric.
    """
    converging = []
    for row in aircraft:
        ct = convergence_time(
            row["current"],
            row["previous"],
            centroid,
            float(row["delta_t_s"]),
        )
        if ct is not None:
            converging.append((ct, str(row["id"])))

    converging.sort(key=lambda item: item[0])

    candidates = []
    for left, right in zip(converging[:-1], converging[1:]):
        ct_low, id_low = left
        ct_high, id_high = right
        delta_ct = ct_high - ct_low
        if delta_ct <= float(delta_ct_threshold_s):
            pair_risk = ct_low + delta_ct
            candidates.append((pair_risk, id_low, id_high))

    if not candidates:
        return CollisionRiskResult(None, None, len(converging))

    candidates.sort(key=lambda item: item[0])
    risk_seconds, id_a, id_b = candidates[0]

    if max_risk_seconds is not None and risk_seconds > float(max_risk_seconds):
        return CollisionRiskResult(None, None, len(converging))

    return CollisionRiskResult(
        float(risk_seconds),
        (id_a, id_b),
        len(converging),
    )


def weather_risk_at_centroid(
    storm_cells: Iterable[Mapping[str, object]],
    centroid: Sequence[float],
    max_risk_seconds: Optional[float] = None,
) -> Optional[float]:
    """Return the minimum convergence time among storm cells approaching a centroid."""
    values = []
    for row in storm_cells:
        ct = convergence_time(
            row["current"],
            row["previous"],
            centroid,
            float(row["delta_t_s"]),
        )
        if ct is not None:
            values.append(ct)

    if not values:
        return None

    risk_seconds = float(min(values))
    if max_risk_seconds is not None and risk_seconds > float(max_risk_seconds):
        return None
    return risk_seconds


def risk_probability(
    risk_seconds: Optional[float],
    zero_risk_cutoff_s: float,
) -> float:
    """Map a time-based metric to a bounded 0..1 worst-case-event risk score."""
    if risk_seconds is None:
        return 0.0
    cutoff = float(zero_risk_cutoff_s)
    if cutoff <= 0:
        raise ValueError("zero_risk_cutoff_s must be positive.")
    return float(
        np.clip(1.0 - float(risk_seconds) / cutoff, 0.0, 1.0)
    )


def combine_risk_probabilities(
    weather_risk: float,
    air_traffic_risk: float,
) -> float:
    """Combine bounded weather and air-traffic risk scores with the complement rule."""
    a = float(np.clip(weather_risk, 0.0, 1.0))
    b = float(np.clip(air_traffic_risk, 0.0, 1.0))
    return float(1.0 - ((1.0 - a) * (1.0 - b)))
