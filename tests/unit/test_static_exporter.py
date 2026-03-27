from pathlib import Path

import pytest

from ms_survey.extraction import parse_excel_workbook, write_normalized_parquet
from ms_survey.static_export import export_static_dashboard_html


def _excel_path() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "data"
        / "CANDLE_ Survey for Member States on National Cancer Data Node Plans(1-17).xlsx"
    )


@pytest.fixture
def sample_dataset_dir(tmp_path: Path) -> Path:
    parsed = parse_excel_workbook(_excel_path())
    write_normalized_parquet(parsed, tmp_path)
    return tmp_path


def test_exporter_writes_single_html_file(
    sample_dataset_dir: Path,
    tmp_path: Path,
) -> None:
    output = tmp_path / "dashboard.html"
    report = export_static_dashboard_html(sample_dataset_dir, output)
    assert output.exists()
    assert report["output_path"] == str(output)
    assert report["size_bytes"] > 0

