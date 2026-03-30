"""Build and serialize payload for single-file static dashboard export."""

from __future__ import annotations

import base64
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import pandas as pd

_RESPONDENTS_FILE = "respondents.parquet"
_QUESTIONS_FILE = "questions.parquet"
_ANSWERS_FILE = "answers.parquet"
_ANSWER_ITEMS_FILE = "answer_items.parquet"

_FORBIDDEN_PII_COLUMNS = {
    "respondent_name",
    "respondent_email",
    "name",
    "email",
}


def build_dashboard_payload(
    dataset_dir: str | Path,
    *,
    fail_if_pii: bool = True,
) -> dict[str, Any]:
    """Build export payload from normalized dataset tables."""
    dataset_dir = Path(dataset_dir)
    respondents = _read_parquet(dataset_dir / _RESPONDENTS_FILE)
    questions = _read_parquet(dataset_dir / _QUESTIONS_FILE)
    answers = _read_parquet(dataset_dir / _ANSWERS_FILE)
    answer_items = _read_parquet(dataset_dir / _ANSWER_ITEMS_FILE)

    _validate_no_pii(respondents, answers, fail_if_pii=fail_if_pii)

    payload = {
        "meta": _build_meta(respondents, questions, answers),
        "respondents": respondents.to_dict(orient="records"),
        "questions": questions.to_dict(orient="records"),
        "answers": answers.to_dict(orient="records"),
        "answer_items": answer_items.to_dict(orient="records"),
        "derived": _build_derived_views(respondents, questions, answers, answer_items),
    }
    return payload


def serialize_payload(
    payload: dict[str, Any],
    *,
    max_bytes: int = 25 * 1024 * 1024,
) -> tuple[str, dict[str, Any]]:
    """Serialize payload into base64 JSON string for embedding in HTML."""
    payload_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    encoded = base64.b64encode(payload_json.encode("utf-8")).decode("ascii")

    size_bytes = len(encoded.encode("utf-8"))
    warnings: list[str] = []
    if size_bytes > max_bytes:
        warnings.append(
            f"Payload exceeds configured threshold ({size_bytes} > {max_bytes})"
        )

    report = {
        "encoding": "base64+json",
        "size_bytes": size_bytes,
        "max_bytes": max_bytes,
        "warnings": warnings,
    }
    return encoded, report


def _read_parquet(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required dataset file not found: {path}")
    return pd.read_parquet(path)


def _validate_no_pii(
    respondents: pd.DataFrame,
    answers: pd.DataFrame,
    *,
    fail_if_pii: bool,
) -> None:
    present = (
        set(respondents.columns).union(set(answers.columns)).intersection(
            _FORBIDDEN_PII_COLUMNS
        )
    )
    if present and fail_if_pii:
        present_list = ", ".join(sorted(present))
        raise ValueError(f"PII column(s) present: {present_list}")


def _build_meta(
    respondents: pd.DataFrame,
    questions: pd.DataFrame,
    answers: pd.DataFrame,
) -> dict[str, Any]:
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "respondent_count": int(len(respondents)),
        "question_count": int(len(questions)),
        "answer_count": int(len(answers)),
        "country_count": int(
            respondents["country_iso"].nunique() if "country_iso" in respondents else 0
        ),
    }


def _build_derived_views(
    respondents: pd.DataFrame,
    questions: pd.DataFrame,
    answers: pd.DataFrame,
    answer_items: pd.DataFrame,
) -> dict[str, Any]:
    """Build pre-computed structures to speed up client-side rendering."""
    section_heatmap = _derive_section_heatmap(answers)
    question_stats = _derive_question_stats(answers)
    country_list = (
        sorted(respondents["country_iso"].dropna().unique().tolist())
        if "country_iso" in respondents
        else []
    )
    return {
        "section_heatmap": section_heatmap,
        "question_stats": question_stats,
        "countries": country_list,
        "section_ids": (
            sorted(questions["section_id"].dropna().unique().tolist())
            if "section_id" in questions
            else []
        ),
        "answer_item_count": int(len(answer_items)),
    }


def _derive_section_heatmap(answers: pd.DataFrame) -> list[dict[str, Any]]:
    if answers.empty:
        return []

    working = answers.copy()
    working["answered_flag"] = working["answer_state"] == "answered"
    grouped = (
        working.groupby(["section_id", "country_iso"], dropna=False)["answered_flag"]
        .mean()
        .reset_index(name="answered_ratio")
    )
    grouped["answered_pct"] = (grouped["answered_ratio"] * 100).round(2)
    grouped = grouped.drop(columns=["answered_ratio"])
    grouped = grouped.sort_values(["section_id", "country_iso"])
    return grouped.to_dict(orient="records")


def _derive_question_stats(answers: pd.DataFrame) -> list[dict[str, Any]]:
    if answers.empty:
        return []
    grouped = (
        answers.groupby(["question_id", "section_id", "question_type"], dropna=False)
        .agg(
            answer_rows=("respondent_id", "count"),
            answered_rows=("answer_state", lambda s: int((s == "answered").sum())),
            country_count=("country_iso", "nunique"),
        )
        .reset_index()
        .sort_values("question_id")
    )
    grouped["answered_pct"] = grouped.apply(
        lambda row: round((row["answered_rows"] / row["answer_rows"] * 100), 2)
        if row["answer_rows"]
        else 0.0,
        axis=1,
    )
    return grouped.to_dict(orient="records")
