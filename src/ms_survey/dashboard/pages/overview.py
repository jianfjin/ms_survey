"""Compatibility overview page that forwards to section heatmap."""

from __future__ import annotations

import streamlit as st

from ms_survey.analytics import FilterCriteria, NormalizedAnalyticsEngine
from ms_survey.dashboard.pages.section_heatmap import render_section_heatmap
from ms_survey.dashboard.runtime import load_dashboard_context


def render_overview(
    engine: NormalizedAnalyticsEngine,
    filters: FilterCriteria,
) -> None:
    """Keep overview route working by rendering section heatmap content."""
    render_section_heatmap(engine, filters)


def _run_standalone() -> None:
    st.title("📊 MS Survey Analytics Dashboard")
    context = load_dashboard_context()
    if context is None:
        return
    engine, filters = context
    try:
        render_overview(engine, filters)
    finally:
        engine.close()


if __name__ == "__main__":
    _run_standalone()

