"""Question analysis page for normalized dataset."""

from __future__ import annotations

import streamlit as st

from ms_survey.analytics import FilterCriteria, NormalizedAnalyticsEngine
from ms_survey.dashboard.components.charts import (
    render_bar_chart,
    render_text_responses,
)
from ms_survey.dashboard.runtime import load_dashboard_context


def render_question_view(
    engine: NormalizedAnalyticsEngine,
    filters: FilterCriteria,
) -> None:
    """Render side-by-side question analysis."""
    st.header("Question Analysis")

    questions = engine.get_questions()
    if questions.empty:
        st.info("No questions available.")
        return

    labels = {
        f"{row.question_id} [{row.section_id}] {str(row.question_prompt)[:70]}": row.question_id
        for row in questions.itertuples()
    }
    selected_label = st.selectbox("Select Question", options=list(labels.keys()))
    question_id = labels[selected_label]

    metadata = engine.get_question_metadata(question_id)
    if metadata is None:
        st.info("Question metadata not found.")
        return

    st.markdown(f"### {metadata['question_id']}")
    st.caption(f"{metadata['section_id']} | {metadata['question_type']}")
    st.write(metadata["question_prompt"])

    distribution = engine.get_question_country_distribution(question_id, filters=filters)
    if distribution.empty:
        st.info("No answer distribution for selected filters.")
    else:
        st.subheader("Country Comparison Table")
        pivot = distribution.pivot_table(
            index="answer_value",
            columns="country_iso",
            values="percentage",
            fill_value=0,
        )
        st.dataframe(pivot, use_container_width=True)

        st.subheader("Top Answers by Country")
        render_bar_chart(
            distribution.sort_values("respondent_count", ascending=False).head(20),
            x_column="answer_value",
            y_column="respondent_count",
            title="Respondent Count by Answer Option",
        )

    if metadata["question_type"] == "text":
        st.subheader("Masked Theme Summary")
        themes = engine.get_text_theme_summary(question_id, filters=filters)
        if themes.empty:
            st.caption("No theme tokens available.")
        else:
            st.dataframe(themes, use_container_width=True)

        st.subheader("Masked Text Samples")
        text_df = engine.get_text_responses(question_id, filters=filters, limit=30)
        render_text_responses(text_df, max_display=10)


def _run_standalone() -> None:
    st.title("📊 MS Survey Analytics Dashboard")
    context = load_dashboard_context()
    if context is None:
        return
    engine, filters = context
    try:
        render_question_view(engine, filters)
    finally:
        engine.close()


if __name__ == "__main__":
    _run_standalone()
