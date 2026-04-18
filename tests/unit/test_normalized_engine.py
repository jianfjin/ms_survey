from pathlib import Path

import pytest

from ms_survey.analytics import FilterCriteria, NormalizedAnalyticsEngine
from ms_survey.extraction import parse_excel_workbook, write_normalized_parquet


def _excel_path() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "data"
        / "CANDLE_ Survey for Member States on National Cancer Data Node Plans(1-17).xlsx"
    )


@pytest.fixture
def normalized_engine(tmp_path: Path) -> NormalizedAnalyticsEngine:
    parsed = parse_excel_workbook(_excel_path())
    write_normalized_parquet(parsed, tmp_path)
    engine = NormalizedAnalyticsEngine(tmp_path)
    try:
        yield engine
    finally:
        engine.close()


def test_get_section_heatmap_returns_section_country_matrix(
    normalized_engine: NormalizedAnalyticsEngine,
) -> None:
    df = normalized_engine.get_section_heatmap()
    assert {"section_id", "country_iso", "answered_pct"}.issubset(df.columns)
    assert not df.empty


def test_country_comparison_handles_more_than_two_countries(
    normalized_engine: NormalizedAnalyticsEngine,
) -> None:
    questions = normalized_engine.get_questions()
    question_id = questions.iloc[0]["question_id"]
    countries = normalized_engine.get_unique_values("country_iso")[:4]
    distribution = normalized_engine.get_question_country_distribution(
        question_id=question_id,
        countries=countries,
        filters=FilterCriteria(),
    )
    assert distribution["country_iso"].nunique() >= 2


def test_country_delta_insights_returns_delta_rows(
    normalized_engine: NormalizedAnalyticsEngine,
) -> None:
    questions = normalized_engine.get_questions()
    question_id = questions.iloc[0]["question_id"]
    countries = normalized_engine.get_unique_values("country_iso")[:3]
    delta = normalized_engine.get_country_delta_insights(
        question_id=question_id,
        countries=countries,
        filters=FilterCriteria(),
    )
    assert set(["answer_value", "delta_pp", "max_country", "min_country"]).issubset(
        delta.columns
    )


def test_question_answer_summary_matches_q004_benchmark_counts(
    normalized_engine: NormalizedAnalyticsEngine,
) -> None:
    assert normalized_engine.get_effective_question_type("q_004") == "multi_select"

    summary = normalized_engine.get_question_answer_summary("q_004")
    assert {
        "answer_value",
        "response_count",
        "respondent_count",
        "percentage",
        "answered_respondent_total",
    }.issubset(summary.columns)

    expected = {
        "Research data": 17,
        "Registry data": 17,
        "Biobank data": 17,
        "Imaging data": 17,
        "Clinical data": 16,
        "Genetic data": 16,
        "Other": 9,
    }
    count_map = {
        str(row.answer_value): int(row.response_count) for row in summary.itertuples()
    }
    assert count_map == expected
    assert int(summary["answered_respondent_total"].iloc[0]) == 17
