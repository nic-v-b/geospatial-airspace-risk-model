# Reproducibility

## Two reproducibility levels

This repository distinguishes between:

1. **Method-level reproducibility** — running the included deterministic synthetic example and regression tests.
2. **Full case-study reproduction** — rebuilding the paper study from the original OpenSky ADS-B and NOAA weather-radar source data.

The first is self-contained. The second requires external source data and the parameter choices documented in the paper.

## Method-level workflow

From the repository root:

    python -m venv .venv
    pip install -e ".[dev]"
    python -m examples.run_synthetic_demo
    pytest -q

The demo constructs a small 3D grid, evaluates an aircraft pair and a moving storm cell at one centroid, converts the time-based metrics to bounded risk scores using the paper's 180 s air-traffic and 1800 s weather zero-risk cutoffs, and combines the two risks.

## Full paper case study

The paper used real ADS-B observations from the OpenSky Network and NOAA weather-radar data. These datasets are not vendored here. A full recreation therefore requires:

- obtaining source data from the original providers;
- applying the preprocessing described in the paper;
- recreating the study airspace-grid configuration and time windows;
- evaluating the risk metric at each grid centroid and time step;
- regenerating the paper-specific figures and selected-centroid analyses.

This repository intentionally does not make network calls or bulk data requests automatically.

## Determinism

The core calculations in the grid and risk modules are deterministic for fixed inputs.
