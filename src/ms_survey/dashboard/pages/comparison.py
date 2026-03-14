"""Comparison page for cross-country analysis."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ms_survey.analytics import AnalyticsEngine, FilterCriteria
from ms_survey.dashboard.components.charts import render_bar_chart
from ms_survey.definition.seed_ncdn_v1 import load_ncdn_v1


def render_comparison(engine: AnalyticsEngine, filters: FilterCriteria) -> None:
    """Render the country comparison page.

    Args:
        engine: AnalyticsEngine instance
        filters: Current filter criteria
    """
    st.header("Cross-Country Comparison")

    # Get available countries
    available_countries = engine.get_unique_values("country")

    if len(available_countries) < 2:
        st.warning("Need at least 2 countries for comparison.")
        return

    # Country selection
    selected_countries = st.multiselect(
        "Select Countries to Compare",
        options=available_countries,
        default=available_countries[:2],
    )

    if len(selected_countries) < 2:
        st.info("Please select at least 2 countries.")
        return

    # Question selection
    survey = load_ncdn_v1()

    question_options = {}
    for section in survey.sections:
        for question in section.questions:
            if question.question_type in ["single_select", "boolean", "multi_select"]:
                label = f"[{section.title}] Q{question.display_number}: {question.prompt[:40]}..."
                question_options[label] = question

    selected_label = st.selectbox(
        "Select Question to Compare",
        options=list(question_options.keys()),
    )
    selected_question = question_options[selected_label]

    st.markdown(f"### Comparing: {selected_question.prompt}")

    # Get comparison data
    comp_df = engine.compare_countries(
        selected_question.question_id,
        selected_countries,
        filters,
    )

    if comp_df.empty:
        st.info("No data available for comparison.")
        return

    # Pivot for side-by-side comparison
    pivot_df = comp_df.pivot_table(
        index="answer_value",
        columns="country",
        values="respondent_count",
        fill_value=0,
    ).reset_index()

    # Display comparison table
    st.subheader("Comparison Table")
    st.dataframe(pivot_df, use_container_width=True)

    # Display side-by-side charts
    st.subheader("Visual Comparison")

    col1, col2 = st.columns(2)

    for idx, country in enumerate(selected_countries[:2]):
        country_data = comp_df[comp_df["country"] == country]

        with col1 if idx == 0 else col2:
            st.markdown(f"**{country}**")
            render_bar_chart(
                country_data,
                x_column="answer_value",
                y_column="respondent_count",
                title=f"",
            )

    # Show differences
    st.subheader("Key Differences")
    _show_differences(comp_df, selected_countries)


def _show_differences(comp_df: pd.DataFrame, countries: list[str]) -> None:
    """Show key differences between countries."""
    if len(countries) != 2:
        st.caption("Differences analysis available for 2-country comparison only.")
        return

    # Calculate percentages for each country
    for country in countries:
        country_data = comp_df[comp_df["country"] == country]
        total = country_data["respondent_count"].sum()
        if total > 0:
            comp_df.loc[comp_df["country"] == country, "percentage"] = (
                comp_df[comp_df["country"] == country]["respondent_count"] / total * 100
            )

    # Find largest difference
    pivot_pct = comp_df.pivot_table(
        index="answer_value",
        columns="country",
        values="percentage",
        fill_value=0,
    )

    if len(pivot_pct.columns) == 2:
        pivot_pct["difference"] = abs(pivot_pct.iloc[:, 0] - pivot_pct.iloc[:, 1])
        largest_diff = pivot_pct["difference"].idxmax()
        diff_value = pivot_pct.loc[largest_diff, "difference"]

        st.write(
            f"**Largest difference:** '{largest_diff}' with {diff_value:.1f} percentage points difference"
        )

        for country in countries:
            pct = pivot_pct.loc[largest_diff, country]
            st.write(f"- {country}: {pct:.1f}%")
