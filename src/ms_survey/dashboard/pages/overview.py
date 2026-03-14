"""Overview page for the dashboard."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ms_survey.analytics import AnalyticsEngine, FilterCriteria
from ms_survey.dashboard.components.charts import render_bar_chart, render_pie_chart


def render_overview(engine: AnalyticsEngine, filters: FilterCriteria) -> None:
    """Render the overview page.

    Args:
        engine: AnalyticsEngine instance
        filters: Current filter criteria
    """
    st.header("Survey Overview")

    # Get summary statistics
    stats = engine.get_summary_stats(filters)

    # Key metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Respondents", stats["total_respondents"])

    with col2:
        countries_count = len(stats["by_country"])
        st.metric("Countries", countries_count)

    with col3:
        roles_count = len(stats["by_role"])
        st.metric("Unique Roles", roles_count)

    st.markdown("---")

    # Country distribution
    st.subheader("Responses by Country")
    if stats["by_country"]:
        country_df = pd.DataFrame(stats["by_country"])
        render_bar_chart(
            country_df,
            x_column="country",
            y_column="count",
            title="Responses by Country",
        )

    # Role distribution
    st.subheader("Responses by Role")
    if stats["by_role"]:
        role_df = pd.DataFrame(stats["by_role"])
        render_pie_chart(
            role_df,
            label_column="role",
            value_column="count",
            title="Distribution by Role",
        )

    # Data source breakdown
    st.subheader("Data Source")
    source_data = {}
    for item in stats["by_country"]:
        source = item["data_source"]
        source_data[source] = source_data.get(source, 0) + item["count"]

    if source_data:
        source_df = pd.DataFrame(
            [{"source": k, "count": v} for k, v in source_data.items()]
        )
        render_pie_chart(
            source_df,
            label_column="source",
            value_column="count",
            title="Original vs Synthetic Data",
        )
