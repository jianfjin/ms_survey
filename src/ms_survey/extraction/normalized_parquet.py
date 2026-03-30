"""Write normalized dashboard datasets to Parquet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ms_survey.extraction.excel_parser import ParsedWorkbook


def write_normalized_parquet(parsed: ParsedWorkbook, output_dir: str | Path) -> None:
    """Write normalized tables to a dataset directory."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    parsed.respondents.to_parquet(out_dir / "respondents.parquet", index=False)
    parsed.questions.to_parquet(out_dir / "questions.parquet", index=False)
    parsed.answers.to_parquet(out_dir / "answers.parquet", index=False)

    answer_items = explode_answer_items(parsed.answers)
    answer_items.to_parquet(out_dir / "answer_items.parquet", index=False)


def explode_answer_items(answers: pd.DataFrame) -> pd.DataFrame:
    """Explode multi-value answers into one-row-per-item shape."""
    if answers.empty:
        return pd.DataFrame(
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

    records: list[dict[str, str | int]] = []

    for _, row in answers.iterrows():
        if row["answer_state"] != "answered":
            continue

        raw_value = row["answer_value_masked"]
        if not isinstance(raw_value, str) or not raw_value.strip():
            continue

        if row["question_type"] in {"multi_select", "ranking"}:
            parts = [part.strip() for part in raw_value.split(";") if part.strip()]
        else:
            parts = [raw_value.strip()]

        for position, part in enumerate(parts, start=1):
            records.append(
                {
                    "respondent_id": row["respondent_id"],
                    "country_iso": row["country_iso"],
                    "section_id": row["section_id"],
                    "question_id": row["question_id"],
                    "question_type": row["question_type"],
                    "item_value": part,
                    "item_position": position,
                }
            )

    return pd.DataFrame(records)

