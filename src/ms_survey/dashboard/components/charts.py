"""Streamlit dashboard components for visualizations."""

from __future__ import annotations

from html import escape
import math

import altair as alt
import pandas as pd
import streamlit as st

_TEAL_PALETTE = ["#115e59", "#0f766e", "#0d9488", "#14b8a6", "#2dd4bf", "#5eead4"]


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


def build_structured_answer_chart(
    df: pd.DataFrame,
    title: str,
    answered_respondent_total: int,
) -> alt.LayerChart:
    """Build a Highcharts-inspired dual-axis bar chart for structured answers."""
    working = df.copy()
    working["answer_value"] = working["answer_value"].astype(str)
    working["response_count"] = working["response_count"].astype(float)
    working["percentage"] = working["percentage"].astype(float)

    count_max = int(working["response_count"].max()) if not working.empty else 0
    domain_anchor = max(count_max, answered_respondent_total, 1)
    count_axis_max = domain_anchor + 1 if count_max >= domain_anchor else domain_anchor

    base = alt.Chart(working).encode(
        x=alt.X(
            "answer_value:N",
            sort=alt.SortField(field="response_count", order="descending"),
            axis=alt.Axis(
                title=None,
                labelAngle=-30,
                labelLimit=220,
                labelFont="Arial",
                labelFontSize=11,
            ),
        )
    )

    bars = base.mark_bar(
        color=_TEAL_PALETTE[1],
        cornerRadiusTopLeft=4,
        cornerRadiusTopRight=4,
    ).encode(
        y=alt.Y(
            "response_count:Q",
            scale=alt.Scale(domain=[0, count_axis_max]),
            axis=alt.Axis(
                title="Total Count",
                titleFont="Arial",
                labelFont="Arial",
                grid=True,
                gridColor="#d8e3e1",
                gridOpacity=0.75,
            ),
        ),
        tooltip=[
            alt.Tooltip("answer_value:N", title="Answer"),
            alt.Tooltip("response_count:Q", title="Total Count", format=".0f"),
            alt.Tooltip("respondent_count:Q", title="Respondents", format=".0f"),
            alt.Tooltip("percentage:Q", title="Percentage", format=".2f"),
        ],
    )

    labels = base.mark_text(
        dy=-7,
        color="#334155",
        font="Arial",
        fontSize=11,
        fontWeight="bold",
    ).encode(
        y=alt.Y("response_count:Q", scale=alt.Scale(domain=[0, count_axis_max])),
        text=alt.Text("response_count:Q", format=".0f"),
    )

    line = base.mark_line(
        color=_TEAL_PALETTE[4],
        point=alt.OverlayMarkDef(size=60, color=_TEAL_PALETTE[5]),
        strokeDash=[4, 2],
    ).encode(
        y=alt.Y(
            "percentage:Q",
            scale=alt.Scale(domain=[0, 100]),
            axis=alt.Axis(
                title="Percentage (%)",
                orient="right",
                titleFont="Arial",
                labelFont="Arial",
                grid=False,
            ),
        )
    )

    return (
        alt.layer(bars, labels, line)
        .resolve_scale(y="independent")
        .properties(title=title, height=420)
        .configure_view(stroke=None)
    )


def render_structured_answer_chart(
    df: pd.DataFrame,
    title: str,
    answered_respondent_total: int,
) -> None:
    """Render Highcharts-inspired chart for structured question summaries."""
    if df.empty:
        st.info("No data available for this chart.")
        return

    chart = build_structured_answer_chart(
        df=df,
        title=title,
        answered_respondent_total=answered_respondent_total,
    )
    st.altair_chart(chart, use_container_width=True)


def build_horizontal_ranked_chart(
    df: pd.DataFrame,
    label_column: str,
    value_column: str,
    title: str,
) -> alt.LayerChart:
    """Build a horizontal ranked bar chart optimized for long labels."""
    working = df[[label_column, value_column]].copy()
    working[label_column] = working[label_column].astype(str)
    working[value_column] = pd.to_numeric(working[value_column], errors="coerce").fillna(0.0)
    working = working.sort_values(value_column, ascending=False).reset_index(drop=True)

    base = alt.Chart(working)
    bars = base.mark_bar(cornerRadiusEnd=4).encode(
        y=alt.Y(
            f"{label_column}:N",
            sort=alt.SortField(field=value_column, order="descending"),
            axis=alt.Axis(title=None, labelFont="Arial", labelFontSize=11, labelLimit=340),
        ),
        x=alt.X(
            f"{value_column}:Q",
            axis=alt.Axis(
                title="Count",
                titleFont="Arial",
                labelFont="Arial",
                grid=True,
                gridColor="#d8e3e1",
                gridOpacity=0.75,
            ),
        ),
        color=alt.Color(f"{value_column}:Q", scale=alt.Scale(scheme="viridis"), legend=None),
        tooltip=[
            alt.Tooltip(f"{label_column}:N", title="Category"),
            alt.Tooltip(f"{value_column}:Q", title="Count", format=".0f"),
        ],
    )

    labels = base.mark_text(
        align="left",
        baseline="middle",
        dx=4,
        color="#0f172a",
        font="Arial",
        fontWeight="bold",
    ).encode(
        y=alt.Y(f"{label_column}:N", sort=alt.SortField(field=value_column, order="descending")),
        x=alt.X(f"{value_column}:Q"),
        text=alt.Text(f"{value_column}:Q", format=".0f"),
    )

    return (
        alt.layer(bars, labels)
        .properties(title=title, height=max(260, min(620, 34 * max(len(working), 6))))
        .configure_view(stroke=None)
    )


def render_horizontal_ranked_chart(
    df: pd.DataFrame,
    label_column: str,
    value_column: str,
    title: str,
) -> None:
    if df.empty:
        st.info("No data available for this chart.")
        return
    st.altair_chart(
        build_horizontal_ranked_chart(
            df=df,
            label_column=label_column,
            value_column=value_column,
            title=title,
        ),
        use_container_width=True,
    )


def build_lollipop_chart(
    df: pd.DataFrame,
    label_column: str,
    value_column: str,
    title: str,
) -> alt.LayerChart:
    """Build a clean lollipop chart for ranked comparisons."""
    working = df[[label_column, value_column]].copy()
    working[label_column] = working[label_column].astype(str)
    working[value_column] = pd.to_numeric(working[value_column], errors="coerce").fillna(0.0)
    working = working.sort_values(value_column, ascending=False).reset_index(drop=True)

    base = alt.Chart(working).encode(
        y=alt.Y(
            f"{label_column}:N",
            sort=alt.SortField(field=value_column, order="descending"),
            axis=alt.Axis(title=None, labelFont="Arial", labelFontSize=11, labelLimit=340),
        ),
        x=alt.X(
            f"{value_column}:Q",
            axis=alt.Axis(
                title="Count",
                titleFont="Arial",
                labelFont="Arial",
                grid=True,
                gridColor="#e2e8f0",
                gridOpacity=0.65,
            ),
        ),
    )
    rules = base.mark_rule(color="#cbd5e1", strokeWidth=2).encode(x2=alt.value(0))
    points = base.mark_circle(size=140, color="#0f766e")
    labels = base.mark_text(
        align="left",
        baseline="middle",
        dx=6,
        color="#0f172a",
        font="Arial",
        fontWeight="bold",
    ).encode(text=alt.Text(f"{value_column}:Q", format=".0f"))

    return (
        alt.layer(rules, points, labels)
        .properties(title=title, height=max(260, min(620, 34 * max(len(working), 6))))
        .configure_view(stroke=None)
    )


def render_lollipop_chart(
    df: pd.DataFrame,
    label_column: str,
    value_column: str,
    title: str,
) -> None:
    if df.empty:
        st.info("No data available for this chart.")
        return
    st.altair_chart(
        build_lollipop_chart(
            df=df,
            label_column=label_column,
            value_column=value_column,
            title=title,
        ),
        use_container_width=True,
    )


def build_gradient_column_chart_with_average(
    df: pd.DataFrame,
    label_column: str,
    value_column: str,
    title: str,
) -> alt.LayerChart:
    """Build a gradient column chart with average reference line."""
    working = df[[label_column, value_column]].copy()
    working[label_column] = working[label_column].astype(str)
    working[value_column] = pd.to_numeric(working[value_column], errors="coerce").fillna(0.0)
    working = working.sort_values(value_column, ascending=False).reset_index(drop=True)

    average_value = float(working[value_column].mean()) if not working.empty else 0.0
    avg_df = pd.DataFrame({"avg": [average_value]})

    bars = alt.Chart(working).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X(
            f"{label_column}:N",
            sort=alt.SortField(field=value_column, order="descending"),
            axis=alt.Axis(title=None, labelAngle=-30, labelFont="Arial", labelFontSize=11, labelLimit=220),
        ),
        y=alt.Y(
            f"{value_column}:Q",
            axis=alt.Axis(
                title="Count",
                titleFont="Arial",
                labelFont="Arial",
                grid=True,
                gridColor="#d8e3e1",
                gridOpacity=0.75,
            ),
        ),
        color=alt.Color(f"{value_column}:Q", scale=alt.Scale(scheme="viridis"), legend=None),
        tooltip=[
            alt.Tooltip(f"{label_column}:N", title="Category"),
            alt.Tooltip(f"{value_column}:Q", title="Count", format=".0f"),
        ],
    )

    rule = alt.Chart(avg_df).mark_rule(color="#dc2626", strokeDash=[6, 4], strokeWidth=2).encode(
        y="avg:Q"
    )
    label = alt.Chart(avg_df).mark_text(
        color="#dc2626",
        font="Arial",
        fontWeight="bold",
        align="right",
        dx=-6,
        dy=-4,
    ).encode(
        y="avg:Q",
        text=alt.value(f"Average ({average_value:.1f})"),
    )

    return (
        alt.layer(bars, rule, label)
        .properties(title=title, height=380)
        .configure_view(stroke=None)
    )


def render_gradient_column_chart_with_average(
    df: pd.DataFrame,
    label_column: str,
    value_column: str,
    title: str,
) -> None:
    if df.empty:
        st.info("No data available for this chart.")
        return
    st.altair_chart(
        build_gradient_column_chart_with_average(
            df=df,
            label_column=label_column,
            value_column=value_column,
            title=title,
        ),
        use_container_width=True,
    )


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


def build_word_cloud_tokens(
    themes: pd.DataFrame,
    min_size: int = 14,
    max_size: int = 44,
) -> list[dict[str, str | int]]:
    """Create deterministic visual token descriptors for a word-cloud style render."""
    if themes.empty:
        return []

    working = (
        themes[["theme", "count"]]
        .copy()
        .dropna(subset=["theme", "count"])
        .astype({"theme": str})
        .sort_values(["count", "theme"], ascending=[False, True])
        .reset_index(drop=True)
    )
    if working.empty:
        return []

    max_count = int(working["count"].max())
    min_count = int(working["count"].min())
    span = max(max_count - min_count, 1)
    tokens: list[dict[str, str | int]] = []
    for idx, row in working.iterrows():
        count = int(row["count"])
        scale = (count - min_count) / span if span else 1.0
        font_size = int(round(min_size + (max_size - min_size) * scale))
        tokens.append(
            {
                "theme": str(row["theme"]),
                "count": count,
                "font_size": font_size,
                "color": _TEAL_PALETTE[idx % len(_TEAL_PALETTE)],
                "weight": 700 if idx < math.ceil(len(working) / 4) else 600,
            }
        )
    return tokens


def render_word_cloud_style(themes: pd.DataFrame, title: str = "Masked Theme Cloud") -> None:
    """Render deterministic word-cloud style view for masked text themes."""
    tokens = build_word_cloud_tokens(themes)
    if not tokens:
        st.info("No theme tokens available.")
        return

    spans = []
    for token in tokens:
        spans.append(
            (
                "<span style=\"display:inline-block;margin:8px 12px;"
                f"font-family:Arial,Helvetica,sans-serif;"
                f"font-size:{int(token['font_size'])}px;"
                f"font-weight:{int(token['weight'])};"
                f"color:{token['color']};"
                "line-height:1.2;\">"
                f"{escape(str(token['theme']))}"
                "</span>"
            )
        )

    cloud_html = (
        "<div style=\"border:none;background:#f7fbfb;border-radius:10px;padding:16px 18px;"
        "min-height:160px;\">"
        f"<div style=\"font-family:Arial,Helvetica,sans-serif;font-size:14px;font-weight:700;"
        f"color:#0f172a;margin-bottom:10px;\">{escape(title)}</div>"
        "<div style=\"display:flex;flex-wrap:wrap;align-items:center;\">"
        + "".join(spans)
        + "</div></div>"
    )
    st.markdown(cloud_html, unsafe_allow_html=True)


def render_text_responses(df: pd.DataFrame, max_display: int | None = None) -> None:
    """Render text responses in an expandable format.

    Args:
        df: DataFrame with text responses
        max_display: Maximum number to show initially. None shows all.
    """
    if df.empty:
        st.info("No text responses available.")
        return

    display_count = len(df) if max_display is None else min(len(df), max_display)
    st.write(f"Showing {display_count} of {len(df)} responses:")

    for _, row in df.head(display_count).iterrows():
        with st.expander(
            f"Response from {row.get('country', 'Unknown')} - {row.get('role', 'Unknown')}"
        ):
            st.write(row.get("text_response", "No text"))

    if max_display is not None and len(df) > max_display:
        st.caption(f"... and {len(df) - max_display} more responses")


def render_heatmap(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    color_column: str,
    title: str,
) -> None:
    """Render a section-country heatmap."""
    if df.empty:
        st.info("No data available for this chart.")
        return

    chart = (
        alt.Chart(df)
        .mark_rect()
        .encode(
            x=alt.X(x_column, sort=None),
            y=alt.Y(y_column, sort=None),
            color=alt.Color(color_column, scale=alt.Scale(scheme="blues")),
            tooltip=[x_column, y_column, color_column],
        )
        .properties(title=title, height=420)
    )
    st.altair_chart(chart, use_container_width=True)
