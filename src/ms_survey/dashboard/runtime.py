"""Shared runtime helpers for Streamlit pages."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from ms_survey.analytics import FilterCriteria, NormalizedAnalyticsEngine
from ms_survey.dashboard.components.filters import render_sidebar_filters


def load_dashboard_context() -> tuple[NormalizedAnalyticsEngine, FilterCriteria] | None:
    """Create engine and filter context for a dashboard page."""
    dataset_dir = st.sidebar.text_input(
        "Dataset Directory",
        value="data/normalized",
        help="Directory containing respondents/questions/answers/answer_items parquet files",
    )

    if not Path(dataset_dir).exists():
        st.error(f"Dataset directory not found: {dataset_dir}")
        st.info(
            "Run `ms-survey build-excel-dataset --input \"data/CANDLE_ Survey for Member States on National Cancer Data Node Plans(1-17).xlsx\" --output-dir data/normalized`"
        )
        return None

    try:
        engine = NormalizedAnalyticsEngine(dataset_dir)
    except Exception as exc:
        st.error(f"Error loading data: {exc}")
        return None

    filters = render_sidebar_filters(engine)
    return engine, filters

