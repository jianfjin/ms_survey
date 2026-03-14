"""Streamlit dashboard components for filters."""

from __future__ import annotations

import streamlit as st

from ms_survey.analytics import FilterCriteria


def render_sidebar_filters(engine) -> FilterCriteria:
    """Render sidebar filters and return filter criteria.

    Args:
        engine: AnalyticsEngine instance

    Returns:
        FilterCriteria based on user selection
    """
    st.sidebar.header("Filters")

    # Get unique values from data
    countries = engine.get_unique_values("country")
    roles = engine.get_unique_values("role")
    data_sources = engine.get_unique_values("data_source")

    # Country filter
    selected_countries = st.sidebar.multiselect(
        "Countries",
        options=countries,
        default=countries,
    )

    # Role filter
    selected_roles = st.sidebar.multiselect(
        "Roles",
        options=roles,
        default=[],
    )

    # Data source filter
    selected_sources = st.sidebar.multiselect(
        "Data Source",
        options=data_sources,
        default=data_sources,
    )

    # Build filter criteria
    filters = FilterCriteria(
        countries=selected_countries if selected_countries else None,
        roles=selected_roles if selected_roles else None,
        data_sources=selected_sources if selected_sources else None,
    )

    # Show filter summary
    st.sidebar.markdown("---")
    st.sidebar.caption(
        f"Active filters: {len([f for f in [selected_countries, selected_roles, selected_sources] if f])}"
    )

    return filters
