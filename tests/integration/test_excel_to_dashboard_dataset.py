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
        assert not heatmap.empty
        assert stats["total_respondents"] > 0
        assert stats["country_count"] > 0
    finally:
        engine.close()

