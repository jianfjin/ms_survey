import pandas as pd

from ms_survey.dashboard.pages.question_view import (
    _format_answer_summary_table,
    _is_structured_question,
)


def test_is_structured_question_handles_supported_types() -> None:
    assert _is_structured_question("single_select")
    assert _is_structured_question("multi_select")
    assert _is_structured_question("ranking")
    assert _is_structured_question("boolean")
    assert not _is_structured_question("text")


def test_format_answer_summary_table_columns() -> None:
    summary = pd.DataFrame(
        [
            {
                "answer_value": "Research data",
                "response_count": 17,
                "respondent_count": 17,
                "percentage": 100.0,
                "answered_respondent_total": 17,
            }
        ]
    )
    formatted = _format_answer_summary_table(summary)
    assert list(formatted.columns) == [
        "answer_value",
        "response_count",
        "respondent_count",
        "percentage",
    ]
