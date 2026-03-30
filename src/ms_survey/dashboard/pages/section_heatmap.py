"""Section heatmap landing page."""

from __future__ import annotations

import streamlit as st

from ms_survey.analytics import FilterCriteria, NormalizedAnalyticsEngine
from ms_survey.dashboard.components.charts import render_heatmap
from ms_survey.dashboard.runtime import load_dashboard_context


def render_section_heatmap(
    engine: NormalizedAnalyticsEngine,
    filters: FilterCriteria,
) -> None:
    """Render section-country answer coverage heatmap."""
    st.header("Section Heatmap")
    st.caption("Coverage by section and country ISO code")

    stats = engine.get_summary_stats(filters)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Respondents", stats["total_respondents"])
    with col2:
        st.metric("Countries", stats["country_count"])
    with col3:
        st.metric("Questions", stats["question_count"])

    heatmap_df = engine.get_section_heatmap(filters)
    if heatmap_df.empty:
        st.info("No section coverage data for the current filters.")
        return

    render_heatmap(
        heatmap_df,
        x_column="country_iso",
        y_column="section_id",
        color_column="answered_pct",
        title="Answered Percentage by Section and Country",
    )

    st.subheader("Most Missing Sections")
    low_coverage = heatmap_df.sort_values("answered_pct", ascending=True).head(10)
    st.dataframe(low_coverage, use_container_width=True)


def _run_standalone() -> None:
    st.title("📊 MS Survey Analytics Dashboard")
    context = load_dashboard_context()
    if context is None:
        return
    engine, filters = context
    try:
        render_section_heatmap(engine, filters)
    finally:
        engine.close()


if __name__ == "__main__":
    _run_standalone()
