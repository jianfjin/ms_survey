from pathlib import Path

from ms_survey.extraction import parse_excel_workbook, write_normalized_parquet
from ms_survey.static_export import export_static_dashboard_html


def _excel_path() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "data"
        / "CANDLE_ Survey for Member States on National Cancer Data Node Plans(1-17).xlsx"
    )


def test_normalized_dataset_exports_static_html(tmp_path: Path) -> None:
    dataset_dir = tmp_path / "normalized"
    parsed = parse_excel_workbook(_excel_path())
    write_normalized_parquet(parsed, dataset_dir)

    output = tmp_path / "dashboard.html"
    report = export_static_dashboard_html(dataset_dir, output)
    html = output.read_text(encoding="utf-8")

    assert "<!doctype html>" in html.lower()
    assert "window.__DATA_B64_GZ__" in html
    assert "<main id=\"app-root\"" in html
    assert "CHART_MODES" in html
    assert "Alternative Biomedical Chart Views" in html
    assert "Masked Text Responses" in html
    assert "question_option_profiles" in html
    assert report["size_bytes"] > 0
