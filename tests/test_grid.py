from geospatial_airspace_risk import AirspaceGridSpec, build_regular_grid, morton3d


def test_regular_grid_shape_and_unique_morton_codes():
    grid = build_regular_grid(
        AirspaceGridSpec(0, 0, 0, 20, 20, 20, 10)
    )

    assert len(grid) == 8
    assert grid["morton_code"].is_unique
    assert grid["centroid_id"].tolist() == list(range(8))


def test_morton_origin():
    assert morton3d(0, 0, 0) == 0
