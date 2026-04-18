"""Question analysis page for normalized dataset."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ms_survey.analytics import FilterCriteria, NormalizedAnalyticsEngine
from ms_survey.dashboard.components.charts import (
    render_gradient_column_chart_with_average,
    render_horizontal_ranked_chart,
    render_lollipop_chart,
    render_structured_answer_chart,
    render_text_responses,
    render_word_cloud_style,
)
from ms_survey.dashboard.runtime import load_dashboard_context

_STRUCTURED_QUESTION_TYPES = {"single_select", "multi_select", "ranking", "boolean"}


def _is_structured_question(question_type: str) -> bool:
    return question_type in _STRUCTURED_QUESTION_TYPES


def _format_answer_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    return df[["answer_value", "response_count", "respondent_count", "percentage"]]


def _render_professional_alternative_charts(
    df: pd.DataFrame,
    label_column: str,
    value_column: str,
) -> None:
    if df.empty:
        return

    st.subheader("Alternative Biomedical Chart Views")
    tab1, tab2, tab3 = st.tabs(
        [
            "Horizontal Bar",
            "Lollipop",
            "Gradient + Average",
        ]
    )

    with tab1:
        render_horizontal_ranked_chart(
            df=df,
            label_column=label_column,
            value_column=value_column,
            title="Horizontal Ranked Distribution",
        )
    with tab2:
        render_lollipop_chart(
            df=df,
            label_column=label_column,
            value_column=value_column,
            title="Lollipop Distribution",
        )
    with tab3:
        render_gradient_column_chart_with_average(
            df=df,
            label_column=label_column,
            value_column=value_column,
            title="Gradient Column Distribution",
        )


def render_question_view(
    engine: NormalizedAnalyticsEngine,
    filters: FilterCriteria,
) -> None:
    """Render question-level analysis."""
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

    effective_type = engine.get_effective_question_type(question_id)
    question_type = effective_type or str(metadata["question_type"])
    st.markdown(f"### {metadata['question_id']}")
    st.caption(f"{metadata['section_id']} | {question_type}")
    st.write(metadata["question_prompt"])

    if _is_structured_question(question_type):
        summary = engine.get_question_answer_summary(question_id, filters=filters)
        if summary.empty:
            st.info("No answer distribution for selected filters.")
            return

        answered_total = int(summary["answered_respondent_total"].iloc[0])
        st.metric("Answered Respondents", answered_total)
        st.caption(
            "Percentages are calculated against the answered-respondent total "
            f"({answered_total}) for this question."
        )

        st.subheader("Answer Distribution")
        render_structured_answer_chart(
            summary,
            title="Response Count by Answer Option",
            answered_respondent_total=answered_total,
        )

        st.subheader("Answer Summary Table")
        st.dataframe(
            _format_answer_summary_table(summary),
            use_container_width=True,
        )
        _render_professional_alternative_charts(
            df=summary,
            label_column="answer_value",
            value_column="response_count",
        )
        return

    st.subheader("Masked Theme Summary")
    themes = engine.get_text_theme_summary(question_id, filters=filters)
    if themes.empty:
        st.caption("No theme tokens available.")
    else:
        render_word_cloud_style(themes, title="Masked Theme Cloud")
        st.dataframe(themes, use_container_width=True)
        _render_professional_alternative_charts(
            df=themes,
            label_column="theme",
            value_column="count",
        )

    st.subheader("Masked Text Samples")
    text_df = engine.get_text_responses(question_id, filters=filters, limit=None)
    render_text_responses(text_df, max_display=None)


def _run_standalone() -> None:
    st.title("MS Survey Analytics Dashboard")
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
