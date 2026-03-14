"""Question view page for the dashboard."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ms_survey.analytics import AnalyticsEngine, FilterCriteria
from ms_survey.dashboard.components.charts import (
    render_bar_chart,
    render_horizontal_bar_chart,
    render_pie_chart,
    render_text_responses,
)
from ms_survey.definition.seed_ncdn_v1 import load_ncdn_v1


def render_question_view(engine: AnalyticsEngine, filters: FilterCriteria) -> None:
    """Render the question view page.

    Args:
        engine: AnalyticsEngine instance
        filters: Current filter criteria
    """
    st.header("Question Analysis")

    # Load survey definition
    survey = load_ncdn_v1()

    # Build question options
    question_options = {}
    for section in survey.sections:
        for question in section.questions:
            label = f"[{section.title}] Q{question.display_number}: {question.prompt[:40]}..."
            question_options[label] = question

    # Question selector
    selected_label = st.selectbox(
        "Select Question",
        options=list(question_options.keys()),
    )
    selected_question = question_options[selected_label]

    # Display question details
    st.markdown(f"### Q{selected_question.display_number}: {selected_question.prompt}")
    st.caption(f"Type: {selected_question.question_type}")

    # Render based on question type
    if selected_question.question_type == "single_select":
        _render_single_select(engine, selected_question, filters)
    elif selected_question.question_type == "multi_select":
        _render_multi_select(engine, selected_question, filters)
    elif selected_question.question_type == "ranking":
        _render_ranking(engine, selected_question, filters)
    elif selected_question.question_type == "boolean":
        _render_boolean(engine, selected_question, filters)
    elif selected_question.question_type == "text":
        _render_text(engine, selected_question, filters)


def _render_single_select(engine, question, filters):
    """Render single select question results."""
    df = engine.get_question_distribution(question.question_id, filters)

    if df.empty:
        st.info("No data available.")
        return

    # Filter to answered responses only
    answered_df = df[df["answer_state"] == "answered"]

    col1, col2 = st.columns(2)

    with col1:
        render_bar_chart(
            answered_df,
            x_column="answer_value",
            y_column="respondent_count",
            title="Responses",
        )

    with col2:
        render_pie_chart(
            answered_df,
            label_column="answer_value",
            value_column="respondent_count",
            title="Distribution",
        )

    # Show data table
    with st.expander("View Data"):
        st.dataframe(answered_df, use_container_width=True)


def _render_multi_select(engine, question, filters):
    """Render multi-select question results."""
    df = engine.get_multi_select_distribution(question.question_id, filters)

    if df.empty:
        st.info("No data available.")
        return

    # Map option IDs to labels
    if question.options:
        option_labels = {opt.option_id: opt.label for opt in question.options}
        df["option_label"] = df["option_id"].map(option_labels)
    else:
        df["option_label"] = df["option_id"]

    render_bar_chart(
        df,
        x_column="option_label",
        y_column="respondent_count",
        title="Option Selection Frequency",
    )

    # Show data table
    with st.expander("View Data"):
        st.dataframe(df, use_container_width=True)


def _render_ranking(engine, question, filters):
    """Render ranking question results."""
    df = engine.get_ranking_distribution(question.question_id, filters)

    if df.empty:
        st.info("No data available.")
        return

    # Map option IDs to labels
    if question.options:
        option_labels = {opt.option_id: opt.label for opt in question.options}
        df["option_label"] = df["option_id"].map(option_labels)
    else:
        df["option_label"] = df["option_id"]

    col1, col2 = st.columns(2)

    with col1:
        render_horizontal_bar_chart(
            df,
            y_column="option_label",
            x_column="average_rank",
            title="Average Rank (lower is better)",
        )

    with col2:
        # Show ranking statistics
        st.subheader("Ranking Statistics")
        stats_df = df[
            ["option_label", "average_rank", "best_rank", "worst_rank"]
        ].copy()
        stats_df["average_rank"] = stats_df["average_rank"].round(2)
        st.dataframe(stats_df, use_container_width=True)


def _render_boolean(engine, question, filters):
    """Render boolean question results."""
    df = engine.get_question_distribution(question.question_id, filters)

    if df.empty:
        st.info("No data available.")
        return

    # Filter to answered responses
    answered_df = df[df["answer_state"] == "answered"].copy()
    answered_df["answer_value"] = answered_df["answer_value"].map(
        {
            "True": "Yes",
            "False": "No",
        }
    )

    col1, col2 = st.columns(2)

    with col1:
        render_bar_chart(
            answered_df,
            x_column="answer_value",
            y_column="respondent_count",
            title="Responses",
        )

    with col2:
        render_pie_chart(
            answered_df,
            label_column="answer_value",
            value_column="respondent_count",
            title="Distribution",
        )


def _render_text(engine, question, filters):
    """Render text question results."""
    df = engine.get_text_responses(question.question_id, filters, limit=50)

    if df.empty:
        st.info("No text responses available.")
        return

    render_text_responses(df, max_display=10)
