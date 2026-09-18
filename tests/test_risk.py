import math

from geospatial_airspace_risk import (
    collision_risk_at_centroid,
    combine_risk_probabilities,
    convergence_time,
    risk_probability,
    weather_risk_at_centroid,
)


def test_convergence_time_for_linear_approach():
    ct = convergence_time(
        current=(5.0, 0.0, 0.0),
        previous=(10.0, 0.0, 0.0),
        centroid=(0.0, 0.0, 0.0),
        delta_t_s=5.0,
    )
    assert math.isclose(ct, 5.0)


def test_non_converging_entity_returns_none():
    assert convergence_time(
        current=(10.0, 0.0, 0.0),
        previous=(5.0, 0.0, 0.0),
        centroid=(0.0, 0.0, 0.0),
        delta_t_s=5.0,
    ) is None


def test_collision_pair_uses_smallest_qualifying_pair_risk():
    result = collision_risk_at_centroid(
        [
            {
                "id": "A",
                "previous": (15.0, 0.0, 0.0),
                "current": (10.0, 0.0, 0.0),
                "delta_t_s": 5.0,
            },
            {
                "id": "B",
                "previous": (16.0, 0.0, 0.0),
                "current": (11.0, 0.0, 0.0),
                "delta_t_s": 5.0,
            },
        ],
        centroid=(0.0, 0.0, 0.0),
        delta_ct_threshold_s=2.0,
    )
    assert result.driving_pair == ("A", "B")
    assert math.isclose(result.risk_seconds, 11.0)


def test_weather_and_combined_scores_are_bounded():
    weather_seconds = weather_risk_at_centroid(
        [
            {
                "id": "S",
                "previous": (20.0, 0.0, 0.0),
                "current": (10.0, 0.0, 0.0),
                "delta_t_s": 5.0,
            }
        ],
        centroid=(0.0, 0.0, 0.0),
    )
    weather = risk_probability(weather_seconds, 180.0)
    air = risk_probability(90.0, 180.0)
    combined = combine_risk_probabilities(weather, air)

    assert 0.0 <= weather <= 1.0
    assert 0.0 <= combined <= 1.0
    assert combined >= max(weather, air)
