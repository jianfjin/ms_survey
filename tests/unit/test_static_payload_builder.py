from pathlib import Path

import pandas as pd
import pytest

from ms_survey.extraction import parse_excel_workbook, write_normalized_parquet
from ms_survey.static_export.payload_builder import (
    build_dashboard_payload,
    serialize_payload,
)


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


def test_payload_contains_required_keys(sample_dataset_dir: Path) -> None:
    payload = build_dashboard_payload(sample_dataset_dir)
    assert set(payload.keys()) >= {
        "meta",
        "respondents",
        "questions",
        "answers",
        "answer_items",
        "derived",
    }


def test_payload_rejects_name_email_columns(tmp_path: Path) -> None:
    respondents = pd.DataFrame(
        [
            {
                "respondent_id": "r1",
                "country_iso": "NL",
                "respondent_name": "Hidden",
            }
        ]
    )
    questions = pd.DataFrame(
        [
            {
                "question_id": "q_001",
                "question_prompt": "Prompt",
                "section_id": "section_a",
                "question_order": 1,
                "question_type": "text",
            }
        ]
    )
    answers = pd.DataFrame(
        [
            {
                "respondent_id": "r1",
                "country_iso": "NL",
                "section_id": "section_a",
                "question_id": "q_001",
                "question_prompt": "Prompt",
                "question_order": 1,
                "question_type": "text",
                "answer_state": "answered",
                "answer_value_masked": "masked",
            }
        ]
    )
    answer_items = pd.DataFrame(
        columns=[
            "respondent_id",
            "country_iso",
            "section_id",
            "question_id",
            "question_type",
            "item_value",
            "item_position",
        ]
    )

    respondents.to_parquet(tmp_path / "respondents.parquet", index=False)
    questions.to_parquet(tmp_path / "questions.parquet", index=False)
    answers.to_parquet(tmp_path / "answers.parquet", index=False)
    answer_items.to_parquet(tmp_path / "answer_items.parquet", index=False)

    with pytest.raises(ValueError, match="PII column"):
        build_dashboard_payload(tmp_path, fail_if_pii=True)


def test_serialize_payload_reports_size_warning_for_large_payload(
    sample_dataset_dir: Path,
) -> None:
    payload = build_dashboard_payload(sample_dataset_dir)
    encoded, report = serialize_payload(payload, max_bytes=512)
    assert encoded
    assert report["warnings"]
    assert report["size_bytes"] > 512

