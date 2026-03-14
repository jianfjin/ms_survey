"""Streamlit dashboard components for visualizations."""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st


def render_bar_chart(
    df: pd.DataFrame, x_column: str, y_column: str, title: str
) -> None:
    """Render a bar chart.

    Args:
        df: DataFrame with data
        x_column: Column for x-axis
        y_column: Column for y-axis
        title: Chart title
    """
    if df.empty:
        st.info("No data available for this chart.")
        return

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(x_column, sort="-y"),
            y=y_column,
            tooltip=[x_column, y_column],
        )
        .properties(
            title=title,
        )
    )

    st.altair_chart(chart, use_container_width=True)


def render_pie_chart(
    df: pd.DataFrame, label_column: str, value_column: str, title: str
) -> None:
    """Render a pie chart.

    Args:
        df: DataFrame with data
        label_column: Column for labels
        value_column: Column for values
        title: Chart title
    """
    if df.empty:
        st.info("No data available for this chart.")
        return

    chart = (
        alt.Chart(df)
        .mark_arc()
        .encode(
            theta=value_column,
            color=label_column,
            tooltip=[label_column, value_column],
        )
        .properties(
            title=title,
        )
    )

    st.altair_chart(chart, use_container_width=True)


def render_horizontal_bar_chart(
    df: pd.DataFrame, y_column: str, x_column: str, title: str
) -> None:
    """Render a horizontal bar chart (useful for rankings).

    Args:
        df: DataFrame with data
        y_column: Column for y-axis (categories)
        x_column: Column for x-axis (values)
        title: Chart title
    """
    if df.empty:
        st.info("No data available for this chart.")
        return

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            y=alt.Y(y_column, sort="-x"),
            x=x_column,
            tooltip=[y_column, x_column],
        )
        .properties(
            title=title,
        )
    )

    st.altair_chart(chart, use_container_width=True)


def render_text_responses(df: pd.DataFrame, max_display: int = 10) -> None:
    """Render text responses in an expandable format.

    Args:
        df: DataFrame with text responses
        max_display: Maximum number to show initially
    """
    if df.empty:
        st.info("No text responses available.")
        return

    st.write(f"Showing {min(len(df), max_display)} of {len(df)} responses:")

    for idx, row in df.head(max_display).iterrows():
        with st.expander(
            f"Response from {row.get('country', 'Unknown')} - {row.get('role', 'Unknown')}"
        ):
            st.write(row.get("text_response", "No text"))

    if len(df) > max_display:
        st.caption(f"... and {len(df) - max_display} more responses")
