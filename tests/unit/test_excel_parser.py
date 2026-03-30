from pathlib import Path

from ms_survey.extraction import parse_excel_workbook


def _excel_path() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "data"
        / "CANDLE_ Survey for Member States on National Cancer Data Node Plans(1-17).xlsx"
    )


def test_parse_excel_drops_name_and_email_columns() -> None:
    parsed = parse_excel_workbook(_excel_path())
    assert "respondent_name" not in parsed.respondents.columns
    assert "respondent_email" not in parsed.respondents.columns


def test_parse_excel_builds_iso_country_and_questions() -> None:
    parsed = parse_excel_workbook(_excel_path())

    assert not parsed.respondents.empty
    assert "country_iso" in parsed.respondents.columns
    assert parsed.respondents["country_iso"].str.len().isin([2, 3]).all()
    assert "question_id" in parsed.questions.columns
    assert not parsed.answers.empty

