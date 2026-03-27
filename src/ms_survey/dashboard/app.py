"""Main Streamlit application for MS Survey Analytics."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Add src to path
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from ms_survey.dashboard.pages.section_heatmap import render_section_heatmap
from ms_survey.dashboard.pages.section_view import render_section_view
from ms_survey.dashboard.pages.question_view import render_question_view
from ms_survey.dashboard.pages.comparison import render_comparison
from ms_survey.dashboard.runtime import load_dashboard_context


# Page configuration
st.set_page_config(
    page_title="MS Survey Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    """Main entry point for the dashboard."""
    st.title("📊 MS Survey Analytics Dashboard")
    st.caption("Analyze and compare survey responses across countries")

    context = load_dashboard_context()
    if context is None:
        return
    engine, filters = context

    # Navigation
    st.sidebar.markdown("---")
    st.sidebar.header("Navigation")

    page = st.sidebar.radio(
        "Select Page",
        options=[
            "Section Heatmap",
            "Section View",
            "Question View",
            "Country Comparison",
        ],
    )

    # Render selected page
    if page == "Section Heatmap":
        render_section_heatmap(engine, filters)
    elif page == "Section View":
        render_section_view(engine, filters)
    elif page == "Question View":
        render_question_view(engine, filters)
    elif page == "Country Comparison":
        render_comparison(engine, filters)

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.caption("MS Survey Analytics v0.1.0")

    # Cleanup
    engine.close()


if __name__ == "__main__":
    main()
