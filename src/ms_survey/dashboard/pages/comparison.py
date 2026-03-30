"""Cross-country comparison page."""

from __future__ import annotations

import streamlit as st

from ms_survey.analytics import FilterCriteria, NormalizedAnalyticsEngine
from ms_survey.dashboard.components.charts import render_bar_chart
from ms_survey.dashboard.runtime import load_dashboard_context


def render_comparison(
    engine: NormalizedAnalyticsEngine,
    filters: FilterCriteria,
) -> None:
    """Render side-by-side N-country comparison."""
    st.header("Country Comparison")

    countries = engine.get_unique_values("country_iso")
    if len(countries) < 2:
        st.warning("Need at least two countries.")
        return

    selected_countries = st.multiselect(
        "Countries",
        options=countries,
        default=countries[: min(3, len(countries))],
    )
    if len(selected_countries) < 2:
        st.info("Select at least two countries.")
        return

    questions = engine.get_questions()
    question_options = {
        f"{row.question_id} [{row.section_id}] {str(row.question_prompt)[:65]}": row.question_id
        for row in questions.itertuples()
    }
    selected_question_label = st.selectbox(
        "Question",
        options=list(question_options.keys()),
    )
    question_id = question_options[selected_question_label]

    distribution = engine.get_question_country_distribution(
        question_id=question_id,
        countries=selected_countries,
        filters=filters,
    )
    if distribution.empty:
        st.info("No comparable answers for selected filters.")
        return

    st.subheader("Percentage Matrix")
    pivot_pct = distribution.pivot_table(
        index="answer_value",
        columns="country_iso",
        values="percentage",
        fill_value=0,
    )
    st.dataframe(pivot_pct, use_container_width=True)

    st.subheader("Counts")
    render_bar_chart(
        distribution.sort_values("respondent_count", ascending=False).head(24),
        x_column="answer_value",
        y_column="respondent_count",
        title="Top Answer Counts Across Selected Countries",
    )

    st.subheader("Largest Differences")
    deltas = engine.get_country_delta_insights(
        question_id=question_id,
        countries=selected_countries,
        filters=filters,
        top_n=10,
    )
    if deltas.empty:
        st.caption("No delta insights available for this question.")
    else:
        st.dataframe(deltas, use_container_width=True)


def _run_standalone() -> None:
    st.title("📊 MS Survey Analytics Dashboard")
    context = load_dashboard_context()
    if context is None:
        return
    engine, filters = context
    try:
        render_comparison(engine, filters)
    finally:
        engine.close()


if __name__ == "__main__":
    _run_standalone()
