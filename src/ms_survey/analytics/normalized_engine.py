"""Analytics engine for normalized dashboard datasets."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

import duckdb
import pandas as pd

_TOKEN_RE = re.compile(r"[a-zA-Z]{3,}")
_STOP_WORDS = {
    "the",
    "and",
    "for",
    "that",
    "with",
    "from",
    "this",
    "there",
    "have",
    "your",
    "what",
    "which",
    "will",
    "into",
    "their",
    "they",
    "are",
    "was",
    "were",
    "not",
    "but",
    "can",
    "has",
    "had",
    "all",
    "any",
    "our",
    "you",
    "about",
}


@dataclass
class FilterCriteria:
    """Filter criteria for normalized analytics."""

    countries: list[str] | None = None
    roles: list[str] | None = None
    sections: list[str] | None = None
    question_types: list[str] | None = None
    data_sources: list[str] | None = None


class NormalizedAnalyticsEngine:
    """DuckDB-backed analytics for normalized Parquet dataset directories."""

    def __init__(self, dataset_dir: str | Path):
        self.dataset_dir = Path(dataset_dir)
        self._validate_dataset_dir()
        self.con = duckdb.connect()
        self._create_views()

    def _validate_dataset_dir(self) -> None:
        required = {"respondents.parquet", "questions.parquet", "answers.parquet", "answer_items.parquet"}
        missing = [name for name in required if not (self.dataset_dir / name).exists()]
        if missing:
            missing_list = ", ".join(sorted(missing))
            raise FileNotFoundError(
                f"Dataset directory is missing required files: {missing_list}. "
                f"Run `ms-survey build-excel-dataset --output-dir {self.dataset_dir}` first."
            )

    def _create_views(self) -> None:
        directory = str(self.dataset_dir).replace("\\", "/")
        self.con.execute(
            f"""
            CREATE OR REPLACE VIEW respondents AS
            SELECT * FROM read_parquet('{directory}/respondents.parquet')
            """
        )
        self.con.execute(
            f"""
            CREATE OR REPLACE VIEW questions AS
            SELECT * FROM read_parquet('{directory}/questions.parquet')
            """
        )
        self.con.execute(
            f"""
            CREATE OR REPLACE VIEW answers AS
            SELECT * FROM read_parquet('{directory}/answers.parquet')
            """
        )
        self.con.execute(
            f"""
            CREATE OR REPLACE VIEW answer_items AS
            SELECT * FROM read_parquet('{directory}/answer_items.parquet')
            """
        )

    def get_unique_values(self, column: str, table: str = "respondents") -> list[str]:
        sql = f"""
            SELECT DISTINCT {column}
            FROM {table}
            WHERE {column} IS NOT NULL AND TRIM(CAST({column} AS VARCHAR)) <> ''
            ORDER BY {column}
        """
        rows = self.con.execute(sql).fetchall()
        return [row[0] for row in rows]

    def get_sections(self) -> pd.DataFrame:
        return self.con.execute(
            """
            SELECT
                section_id,
                COUNT(*) AS question_count
            FROM questions
            GROUP BY section_id
            ORDER BY section_id
            """
        ).fetchdf()

    def get_questions(self, section_id: str | None = None) -> pd.DataFrame:
        sql = """
            SELECT DISTINCT
                question_id,
                question_prompt,
                section_id,
                question_type,
                question_order
            FROM questions
        """
        if section_id:
            section_id = section_id.replace("'", "''")
            sql += f" WHERE section_id = '{section_id}'"
        sql += " ORDER BY question_order"
        return self.con.execute(sql).fetchdf()

    def get_question_metadata(self, question_id: str) -> dict[str, Any] | None:
        question_id = question_id.replace("'", "''")
        df = self.con.execute(
            f"""
            SELECT question_id, question_prompt, section_id, question_type, question_order
            FROM questions
            WHERE question_id = '{question_id}'
            LIMIT 1
            """
        ).fetchdf()
        if df.empty:
            return None
        return df.iloc[0].to_dict()

    def get_summary_stats(
        self,
        filters: FilterCriteria | None = None,
    ) -> dict[str, Any]:
        filtered_answers = self._load_answers(filters=filters)
        if filtered_answers.empty:
            return {
                "total_respondents": 0,
                "country_count": 0,
                "question_count": 0,
                "by_country": [],
                "by_role": [],
            }

        by_country = (
            filtered_answers.groupby("country_iso", dropna=False)["respondent_id"]
            .nunique()
            .reset_index(name="count")
            .sort_values("country_iso")
        )

        by_role = (
            filtered_answers.dropna(subset=["role"])
            .groupby("role")["respondent_id"]
            .nunique()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )

        return {
            "total_respondents": int(filtered_answers["respondent_id"].nunique()),
            "country_count": int(filtered_answers["country_iso"].nunique()),
            "question_count": int(filtered_answers["question_id"].nunique()),
            "by_country": by_country.to_dict("records"),
            "by_role": by_role.to_dict("records"),
        }

    def get_section_heatmap(
        self,
        filters: FilterCriteria | None = None,
    ) -> pd.DataFrame:
        df = self._load_answers(filters=filters)
        if df.empty:
            return pd.DataFrame(
                columns=["section_id", "country_iso", "answered_pct", "respondents_answered"]
            )

        working = df.copy()
        working["answered_flag"] = working["answer_state"] == "answered"
        working["answered_respondent"] = working["respondent_id"].where(
            working["answered_flag"], None
        )
        result = (
            working.groupby(["section_id", "country_iso"], dropna=False)
            .agg(
                answered_pct=(
                    "answered_flag",
                    lambda series: round(float(series.mean()) * 100, 2),
                ),
                respondents_answered=("answered_respondent", "nunique"),
            )
            .reset_index()
            .sort_values(["section_id", "country_iso"])
        )
        return result

    def get_section_country_summary(
        self,
        section_id: str,
        filters: FilterCriteria | None = None,
    ) -> pd.DataFrame:
        df = self._load_answers(filters=filters, section_id=section_id)
        if df.empty:
            return pd.DataFrame(
                columns=[
                    "question_id",
                    "question_prompt",
                    "question_type",
                    "countries_answered",
                    "country_iso_list",
                    "answered_count",
                    "total_count",
                    "answered_pct",
                ]
            )

        records: list[dict[str, Any]] = []
        for (question_id, prompt, q_type), question_df in df.groupby(
            ["question_id", "question_prompt", "question_type"], dropna=False
        ):
            answered_df = question_df[question_df["answer_state"] == "answered"]
            countries = sorted(
                [
                    country
                    for country in answered_df["country_iso"].dropna().unique().tolist()
                    if country
                ]
            )
            answered_count = int(len(answered_df))
            total_count = int(len(question_df))
            answered_pct = round((answered_count / total_count) * 100, 2) if total_count else 0.0
            records.append(
                {
                    "question_id": question_id,
                    "question_prompt": prompt,
                    "question_type": q_type,
                    "countries_answered": len(countries),
                    "country_iso_list": ", ".join(countries),
                    "answered_count": answered_count,
                    "total_count": total_count,
                    "answered_pct": answered_pct,
                }
            )

        return pd.DataFrame(records).sort_values("question_id").reset_index(drop=True)

    def get_question_country_distribution(
        self,
        question_id: str,
        countries: list[str] | None = None,
        filters: FilterCriteria | None = None,
    ) -> pd.DataFrame:
        df = self._load_answers(filters=filters, question_id=question_id, countries=countries)
        if df.empty:
            return pd.DataFrame(
                columns=["country_iso", "answer_value", "respondent_count", "percentage"]
            )

        question_type = str(df.iloc[0]["question_type"])
        if question_type in {"multi_select", "ranking"}:
            answer_df = self._load_answer_items(
                filters=filters, question_id=question_id, countries=countries
            )
            if answer_df.empty:
                return pd.DataFrame(
                    columns=["country_iso", "answer_value", "respondent_count", "percentage"]
                )
            grouped = (
                answer_df.groupby(["country_iso", "item_value"])["respondent_id"]
                .nunique()
                .reset_index(name="respondent_count")
                .rename(columns={"item_value": "answer_value"})
            )
            totals = (
                answer_df.groupby("country_iso")["respondent_id"]
                .nunique()
                .reset_index(name="total")
            )
        else:
            answered = df[df["answer_state"] == "answered"].copy()
            grouped = (
                answered.groupby(["country_iso", "answer_value_masked"])["respondent_id"]
                .nunique()
                .reset_index(name="respondent_count")
                .rename(columns={"answer_value_masked": "answer_value"})
            )
            totals = (
                answered.groupby("country_iso")["respondent_id"]
                .nunique()
                .reset_index(name="total")
            )

        if grouped.empty:
            return pd.DataFrame(
                columns=["country_iso", "answer_value", "respondent_count", "percentage"]
            )

        result = grouped.merge(totals, on="country_iso", how="left")
        result["percentage"] = result.apply(
            lambda row: round((row["respondent_count"] / row["total"]) * 100, 2)
            if row["total"]
            else 0.0,
            axis=1,
        )
        return result.drop(columns=["total"]).sort_values(
            ["country_iso", "respondent_count"], ascending=[True, False]
        )

    def get_country_delta_insights(
        self,
        question_id: str,
        countries: list[str],
        filters: FilterCriteria | None = None,
        top_n: int = 5,
    ) -> pd.DataFrame:
        distribution = self.get_question_country_distribution(
            question_id=question_id,
            countries=countries,
            filters=filters,
        )
        if distribution.empty or len(countries) < 2:
            return pd.DataFrame(columns=["answer_value", "delta_pp", "max_country", "min_country"])

        pivot = distribution.pivot_table(
            index="answer_value",
            columns="country_iso",
            values="percentage",
            fill_value=0.0,
        )
        max_country = pivot.idxmax(axis=1)
        min_country = pivot.idxmin(axis=1)
        delta_pp = pivot.max(axis=1) - pivot.min(axis=1)
        pivot["delta_pp"] = delta_pp
        pivot["max_country"] = max_country
        pivot["min_country"] = min_country

        result = (
            pivot[["delta_pp", "max_country", "min_country"]]
            .reset_index()
            .sort_values("delta_pp", ascending=False)
            .head(top_n)
        )
        result["delta_pp"] = result["delta_pp"].round(2)
        return result

    def get_text_responses(
        self,
        question_id: str,
        filters: FilterCriteria | None = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        df = self._load_answers(filters=filters, question_id=question_id)
        if df.empty:
            return pd.DataFrame(columns=["respondent_id", "country_iso", "role", "text_response"])
        text_df = df[
            (df["question_type"] == "text")
            & (df["answer_state"] == "answered")
            & (df["answer_value_masked"].notna())
            & (df["answer_value_masked"].astype(str).str.strip() != "")
        ][["respondent_id", "country_iso", "role", "answer_value_masked"]].copy()
        text_df = text_df.rename(columns={"answer_value_masked": "text_response"})
        return text_df.head(limit)

    def get_text_theme_summary(
        self,
        question_id: str,
        filters: FilterCriteria | None = None,
        top_n: int = 12,
    ) -> pd.DataFrame:
        text_responses = self.get_text_responses(question_id=question_id, filters=filters, limit=2000)
        if text_responses.empty:
            return pd.DataFrame(columns=["theme", "count"])

        token_counts: dict[str, int] = {}
        for value in text_responses["text_response"].astype(str):
            for token in _TOKEN_RE.findall(value.lower()):
                if token in _STOP_WORDS:
                    continue
                token_counts[token] = token_counts.get(token, 0) + 1

        if not token_counts:
            return pd.DataFrame(columns=["theme", "count"])

        theme_df = (
            pd.DataFrame(
                [{"theme": token, "count": count} for token, count in token_counts.items()]
            )
            .sort_values("count", ascending=False)
            .head(top_n)
            .reset_index(drop=True)
        )
        return theme_df

    def _load_answers(
        self,
        filters: FilterCriteria | None = None,
        section_id: str | None = None,
        question_id: str | None = None,
        countries: list[str] | None = None,
    ) -> pd.DataFrame:
        sql = """
            SELECT
                a.respondent_id,
                a.country_iso,
                a.section_id,
                a.question_id,
                a.question_prompt,
                a.question_type,
                a.question_order,
                a.answer_state,
                a.answer_value_masked,
                r.role,
                r.data_source
            FROM answers a
            LEFT JOIN respondents r
                ON r.respondent_id = a.respondent_id
        """
        conditions: list[str] = []

        if section_id:
            conditions.append(f"a.section_id = '{_escape_sql(section_id)}'")
        if question_id:
            conditions.append(f"a.question_id = '{_escape_sql(question_id)}'")

        selected_countries = countries or (filters.countries if filters else None)
        if selected_countries:
            conditions.append(f"a.country_iso IN ({_to_sql_list(selected_countries)})")

        if filters:
            if filters.roles:
                conditions.append(f"r.role IN ({_to_sql_list(filters.roles)})")
            if filters.sections:
                conditions.append(f"a.section_id IN ({_to_sql_list(filters.sections)})")
            if filters.question_types:
                conditions.append(
                    f"a.question_type IN ({_to_sql_list(filters.question_types)})"
                )
            if filters.data_sources:
                conditions.append(f"r.data_source IN ({_to_sql_list(filters.data_sources)})")

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        return self.con.execute(sql).fetchdf()

    def _load_answer_items(
        self,
        filters: FilterCriteria | None = None,
        question_id: str | None = None,
        countries: list[str] | None = None,
    ) -> pd.DataFrame:
        sql = """
            SELECT
                i.respondent_id,
                i.country_iso,
                i.section_id,
                i.question_id,
                i.question_type,
                i.item_value,
                i.item_position,
                r.role,
                r.data_source
            FROM answer_items i
            LEFT JOIN respondents r
                ON r.respondent_id = i.respondent_id
        """
        conditions: list[str] = []
        if question_id:
            conditions.append(f"i.question_id = '{_escape_sql(question_id)}'")

        selected_countries = countries or (filters.countries if filters else None)
        if selected_countries:
            conditions.append(f"i.country_iso IN ({_to_sql_list(selected_countries)})")

        if filters:
            if filters.roles:
                conditions.append(f"r.role IN ({_to_sql_list(filters.roles)})")
            if filters.sections:
                conditions.append(f"i.section_id IN ({_to_sql_list(filters.sections)})")
            if filters.question_types:
                conditions.append(
                    f"i.question_type IN ({_to_sql_list(filters.question_types)})"
                )
            if filters.data_sources:
                conditions.append(f"r.data_source IN ({_to_sql_list(filters.data_sources)})")

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        return self.con.execute(sql).fetchdf()

    def close(self) -> None:
        self.con.close()

    def __enter__(self) -> "NormalizedAnalyticsEngine":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


def _escape_sql(value: str) -> str:
    return value.replace("'", "''")


def _to_sql_list(values: list[str]) -> str:
    escaped = [f"'{_escape_sql(value)}'" for value in values]
    return ", ".join(escaped)
