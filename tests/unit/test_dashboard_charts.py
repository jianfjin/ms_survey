import pandas as pd

from ms_survey.dashboard.components.charts import (
    build_gradient_column_chart_with_average,
    build_horizontal_ranked_chart,
    build_lollipop_chart,
    build_structured_answer_chart,
    build_word_cloud_tokens,
)


def test_build_structured_answer_chart_has_dual_axes_and_labels() -> None:
    df = pd.DataFrame(
        [
            {"answer_value": "Research data", "response_count": 17, "respondent_count": 17, "percentage": 100.0},
            {"answer_value": "Clinical data", "response_count": 16, "respondent_count": 16, "percentage": 94.12},
            {"answer_value": "Other", "response_count": 9, "respondent_count": 9, "percentage": 52.94},
        ]
    )
    chart = build_structured_answer_chart(
        df=df,
        title="Response Count by Answer Option",
        answered_respondent_total=17,
    )
    spec = chart.to_dict()

    assert "layer" in spec
    assert len(spec["layer"]) == 3
    y_titles = [
        layer["encoding"]["y"]["axis"]["title"]
        for layer in spec["layer"]
        if "encoding" in layer and "y" in layer["encoding"] and "axis" in layer["encoding"]["y"]
    ]
    assert "Total Count" in y_titles
    assert "Percentage (%)" in y_titles
    assert spec["config"]["view"]["stroke"] is None


def test_build_word_cloud_tokens_is_deterministic() -> None:
    themes = pd.DataFrame(
        [
            {"theme": "data", "count": 12},
            {"theme": "registry", "count": 9},
            {"theme": "genetic", "count": 6},
        ]
    )
    first = build_word_cloud_tokens(themes)
    second = build_word_cloud_tokens(themes)

    assert first == second
    assert first[0]["font_size"] >= first[1]["font_size"] >= first[2]["font_size"]


def test_build_horizontal_ranked_chart_and_lollipop_specs() -> None:
    df = pd.DataFrame(
        [
            {"label": "Research data", "count": 17},
            {"label": "Registry data", "count": 16},
            {"label": "Other", "count": 9},
        ]
    )

    horizontal = build_horizontal_ranked_chart(
        df=df,
        label_column="label",
        value_column="count",
        title="Horizontal",
    ).to_dict()
    lollipop = build_lollipop_chart(
        df=df,
        label_column="label",
        value_column="count",
        title="Lollipop",
    ).to_dict()

    assert len(horizontal["layer"]) == 2
    assert horizontal["layer"][0]["mark"]["type"] == "bar"
    assert len(lollipop["layer"]) == 3
    assert lollipop["layer"][0]["mark"]["type"] == "rule"


def test_build_gradient_column_chart_includes_average_rule() -> None:
    df = pd.DataFrame(
        [
            {"label": "A", "count": 17},
            {"label": "B", "count": 16},
            {"label": "C", "count": 9},
        ]
    )
    chart = build_gradient_column_chart_with_average(
        df=df,
        label_column="label",
        value_column="count",
        title="Gradient",
    ).to_dict()
    assert len(chart["layer"]) == 3
    assert chart["layer"][1]["mark"]["type"] == "rule"
