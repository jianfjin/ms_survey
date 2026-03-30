"""Section analysis page for normalized dashboard dataset."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ms_survey.analytics import FilterCriteria, NormalizedAnalyticsEngine
from ms_survey.dashboard.components.charts import render_bar_chart
from ms_survey.dashboard.runtime import load_dashboard_context


def render_section_view(
    engine: NormalizedAnalyticsEngine,
    filters: FilterCriteria,
) -> None:
    """Render section-level aggregated view."""
    st.header("Section Analysis")

    sections_df = engine.get_sections()
    if sections_df.empty:
        st.info("No sections available in dataset.")
        return

    section_id = st.selectbox("Select Section", options=sections_df["section_id"].tolist())
    summary_df = engine.get_section_country_summary(section_id, filters)
    if summary_df.empty:
        st.info("No data for the selected section and filters.")
        return

    st.caption(f"{len(summary_df)} questions in {section_id}")
    st.dataframe(
        summary_df[
            [
                "question_id",
                "question_type",
                "countries_answered",
                "country_iso_list",
                "answered_count",
                "total_count",
                "answered_pct",
            ]
        ],
        use_container_width=True,
    )

    chart_df = pd.DataFrame(
        {
            "question_id": summary_df["question_id"],
            "countries_answered": summary_df["countries_answered"],
        }
    )
    render_bar_chart(
        chart_df,
        x_column="question_id",
        y_column="countries_answered",
        title="Countries Answered per Question",
    )


def _run_standalone() -> None:
    st.title("📊 MS Survey Analytics Dashboard")
    context = load_dashboard_context()
    if context is None:
        return
    engine, filters = context
    try:
        render_section_view(engine, filters)
    finally:
        engine.close()


if __name__ == "__main__":
    _run_standalone()
