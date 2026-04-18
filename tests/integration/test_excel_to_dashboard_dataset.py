from pathlib import Path

from ms_survey.analytics import NormalizedAnalyticsEngine
from ms_survey.extraction import parse_excel_workbook, write_normalized_parquet


def _excel_path() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "data"
        / "CANDLE_ Survey for Member States on National Cancer Data Node Plans(1-17).xlsx"
    )


def test_excel_pipeline_outputs_aggregate_ready_tables(tmp_path: Path) -> None:
    parsed = parse_excel_workbook(_excel_path())
    write_normalized_parquet(parsed, tmp_path)

    engine = NormalizedAnalyticsEngine(tmp_path)
    try:
        heatmap = engine.get_section_heatmap()
        stats = engine.get_summary_stats()
        summary = engine.get_question_answer_summary("q_004")
        assert not heatmap.empty
        assert stats["total_respondents"] > 0
        assert stats["country_count"] > 0
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
            str(row.answer_value): int(row.response_count)
            for row in summary.itertuples()
        }
        assert count_map == expected
    finally:
        engine.close()
