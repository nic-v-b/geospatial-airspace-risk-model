"""Run a deterministic synthetic demonstration of the paper methodology."""

from geospatial_airspace_risk import (
    AirspaceGridSpec,
    build_regular_grid,
    collision_risk_at_centroid,
    combine_risk_probabilities,
    risk_probability,
    weather_risk_at_centroid,
)


def main() -> None:
    grid = build_regular_grid(
        AirspaceGridSpec(
            x_min=0,
            y_min=0,
            z_min=0,
            x_max=3000,
            y_max=3000,
            z_max=1500,
            resolution_m=500,
        )
    )

    centroid = (1500.0, 1500.0, 750.0)

    aircraft = [
        {
            "id": "A1",
            "previous": (500.0, 1500.0, 750.0),
            "current": (750.0, 1500.0, 750.0),
            "delta_t_s": 5.0,
        },
        {
            "id": "A2",
            "previous": (2500.0, 1500.0, 750.0),
            "current": (2250.0, 1500.0, 750.0),
            "delta_t_s": 5.0,
        },
    ]

    storms = [
        {
            "id": "S1",
            "previous": (1500.0, 3000.0, 1000.0),
            "current": (1500.0, 2750.0, 1000.0),
            "delta_t_s": 5.0,
        }
    ]

    collision = collision_risk_at_centroid(
        aircraft,
        centroid,
        delta_ct_threshold_s=5.0,
        max_risk_seconds=180.0,
    )
    weather_seconds = weather_risk_at_centroid(
        storms,
        centroid,
        max_risk_seconds=1800.0,
    )

    air_score = risk_probability(collision.risk_seconds, 180.0)
    weather_score = risk_probability(weather_seconds, 1800.0)
    combined_score = combine_risk_probabilities(weather_score, air_score)

    print(f"Grid centroids: {len(grid):,}")
    print(f"Collision risk (s): {collision.risk_seconds}")
    print(f"Driving pair: {collision.driving_pair}")
    print(f"Weather risk (s): {weather_seconds}")
    print(f"Air-traffic risk score: {air_score:.4f}")
    print(f"Weather risk score: {weather_score:.4f}")
    print(f"Combined risk score: {combined_score:.4f}")


if __name__ == "__main__":
    main()
