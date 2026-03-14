"""Section view page for the dashboard."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ms_survey.analytics import AnalyticsEngine, FilterCriteria
from ms_survey.dashboard.components.charts import render_bar_chart
from ms_survey.definition.seed_ncdn_v1 import load_ncdn_v1


def render_section_view(engine: AnalyticsEngine, filters: FilterCriteria) -> None:
    """Render the section view page.

    Args:
        engine: AnalyticsEngine instance
        filters: Current filter criteria
    """
    st.header("Section Analysis")

    # Load survey definition
    survey = load_ncdn_v1()

    # Section selector
    section_options = {s.title: s.section_id for s in survey.sections}
    selected_title = st.selectbox(
        "Select Section",
        options=list(section_options.keys()),
    )
    selected_section_id = section_options[selected_title]

    # Find the section
    section = next(s for s in survey.sections if s.section_id == selected_section_id)

    st.markdown(f"### {section.title}")
    st.caption(f"{len(section.questions)} questions in this section")

    # Get section summary
    section_summary = engine.get_section_summary(selected_section_id, filters)

    if not section_summary.empty:
        st.subheader("Question Summary")

        # Create a summary table
        summary_data = []
        for question in section.questions:
            q_data = section_summary[
                section_summary["question_id"] == question.question_id
            ]
            answered = q_data[q_data["answer_state"] == "answered"][
                "respondent_count"
            ].sum()
            total = q_data["respondent_count"].sum()
            completion = (answered / total * 100) if total > 0 else 0

            summary_data.append(
                {
                    "Question": f"Q{question.display_number}: {question.prompt[:50]}...",
                    "Type": question.question_type,
                    "Responses": int(answered),
                    "Completion": f"{completion:.1f}%",
                }
            )

        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)

        # Show completion chart
        st.subheader("Completion Rate by Question")
        completion_df = pd.DataFrame(
            [
                {
                    "question": f"Q{q.display_number}",
                    "completion": float(
                        next(
                            (
                                item["Completion"].rstrip("%")
                                for item in summary_data
                                if item["Question"].startswith(f"Q{q.display_number}")
                            ),
                            0,
                        )
                    ),
                }
                for q in section.questions
            ]
        )

        render_bar_chart(
            completion_df,
            x_column="question",
            y_column="completion",
            title="Completion Rate (%)",
        )
    else:
        st.info("No data available for this section with current filters.")
