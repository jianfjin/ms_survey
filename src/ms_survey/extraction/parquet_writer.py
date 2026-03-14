"""Parquet writer for survey responses with data source flagging."""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Literal

import pyarrow as pa
import pyarrow.parquet as pq

from ms_survey.responses.models import (
    Answer,
    BooleanAnswer,
    CountryResponse,
    MultiSelectAnswer,
    RankingAnswer,
    SingleSelectAnswer,
    TextAnswer,
)


def responses_to_parquet(
    responses: list[CountryResponse],
    output_path: str,
    data_source: Literal["original", "synthetic"],
    timestamp: datetime | None = None,
) -> None:
    """Write survey responses to Parquet file with data source flag.

    Args:
        responses: List of CountryResponse objects
        output_path: Path to write the Parquet file
        data_source: Either "original" or "synthetic"
        timestamp: Optional timestamp for the data (defaults to now)
    """
    if timestamp is None:
        timestamp = datetime.now()

    # Convert responses to flat records
    records = []
    for response in responses:
        base_record = {
            "respondent_id": str(uuid.uuid4()),
            "country": response.country,
            "data_source": data_source,
            "timestamp": timestamp,
            "respondent_name": response.metadata.respondent_name
            if response.metadata
            else None,
            "respondent_email": response.metadata.respondent_email
            if response.metadata
            else None,
            "role": response.metadata.role if response.metadata else None,
            "organization": response.metadata.organization
            if response.metadata
            else None,
        }

        # Add answers as separate columns
        for answer in response.answers:
            answer_data = _serialize_answer(answer)
            record = {**base_record, **answer_data}
            records.append(record)

    # Create PyArrow table
    if not records:
        # Write empty table with correct schema
        table = _create_empty_table(data_source)
    else:
        table = pa.Table.from_pylist(records)

    # Write to Parquet
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, output_path)


def _serialize_answer(answer: Answer) -> dict:
    """Serialize an answer into a flat dictionary."""
    base = {
        "question_id": answer.question_id,
        "answer_state": answer.state.value,
        "answer_type": answer.answer_type,
    }

    if isinstance(answer, SingleSelectAnswer):
        base["answer_value"] = answer.option_id
    elif isinstance(answer, MultiSelectAnswer):
        base["answer_value"] = (
            ",".join(answer.option_ids) if answer.option_ids else None
        )
    elif isinstance(answer, RankingAnswer):
        base["answer_value"] = ",".join(answer.ranking) if answer.ranking else None
    elif isinstance(answer, TextAnswer):
        base["answer_value"] = answer.text
    elif isinstance(answer, BooleanAnswer):
        base["answer_value"] = str(answer.value) if answer.value is not None else None
    else:
        base["answer_value"] = None

    return base


def _create_empty_table(data_source: str) -> pa.Table:
    """Create an empty table with the correct schema."""
    schema = pa.schema(
        [
            ("respondent_id", pa.string()),
            ("country", pa.string()),
            ("data_source", pa.string()),
            ("timestamp", pa.timestamp("us")),
            ("respondent_name", pa.string()),
            ("respondent_email", pa.string()),
            ("role", pa.string()),
            ("organization", pa.string()),
            ("question_id", pa.string()),
            ("answer_state", pa.string()),
            ("answer_type", pa.string()),
            ("answer_value", pa.string()),
        ]
    )
    return pa.table(
        [[] for _ in schema.names],
        schema=schema,
    )


def merge_parquet_files(
    input_paths: list[str],
    output_path: str,
) -> None:
    """Merge multiple Parquet files into one.

    Args:
        input_paths: List of Parquet file paths to merge
        output_path: Path for the merged output file
    """
    tables = [pq.read_table(p) for p in input_paths]
    merged = pa.concat_tables(tables)
    pq.write_table(merged, output_path)
