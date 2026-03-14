"""Main Streamlit application for MS Survey Analytics."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Add src to path
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from ms_survey.analytics import AnalyticsEngine
from ms_survey.dashboard.components.filters import render_sidebar_filters
from ms_survey.dashboard.pages.overview import render_overview
from ms_survey.dashboard.pages.section_view import render_section_view
from ms_survey.dashboard.pages.question_view import render_question_view
from ms_survey.dashboard.pages.comparison import render_comparison


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

    # Initialize analytics engine
    parquet_path = st.sidebar.text_input(
        "Data File",
        value="data/synthetic_responses.parquet",
        help="Path to the Parquet file with survey responses",
    )

    # Check if file exists
    if not Path(parquet_path).exists():
        st.error(f"Data file not found: {parquet_path}")
        st.info("Run `ms-survey generate-synthetic` to create sample data.")
        return

    try:
        engine = AnalyticsEngine(parquet_path)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return

    # Render sidebar filters
    filters = render_sidebar_filters(engine)

    # Navigation
    st.sidebar.markdown("---")
    st.sidebar.header("Navigation")

    page = st.sidebar.radio(
        "Select Page",
        options=[
            "Overview",
            "Section View",
            "Question View",
            "Country Comparison",
        ],
    )

    # Render selected page
    if page == "Overview":
        render_overview(engine, filters)
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
