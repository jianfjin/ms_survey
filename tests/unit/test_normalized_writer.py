from pathlib import Path

import pandas as pd

from ms_survey.extraction import parse_excel_workbook, write_normalized_parquet


def _excel_path() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "data"
        / "CANDLE_ Survey for Member States on National Cancer Data Node Plans(1-17).xlsx"
    )


def test_write_normalized_parquet_creates_expected_tables(tmp_path: Path) -> None:
    parsed = parse_excel_workbook(_excel_path())
    write_normalized_parquet(parsed, tmp_path)

    respondents = tmp_path / "respondents.parquet"
    questions = tmp_path / "questions.parquet"
    answers = tmp_path / "answers.parquet"
    answer_items = tmp_path / "answer_items.parquet"

    assert respondents.exists()
    assert questions.exists()
    assert answers.exists()
    assert answer_items.exists()

    exploded = pd.read_parquet(answer_items)
    assert not exploded.empty

