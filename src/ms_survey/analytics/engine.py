"""DuckDB-based analytics engine for survey data."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from ms_survey.definition.seed_ncdn_v1 import load_ncdn_v1
from ms_survey.definition.models import SurveyDefinition


@dataclass
class FilterCriteria:
    """Filter criteria for survey responses."""

    countries: list[str] | None = None
    roles: list[str] | None = None
    stakeholder_groups: list[str] | None = None
    data_sources: list[str] | None = None

    def to_sql_where(self) -> str | None:
        """Convert filters to SQL WHERE clause."""
        conditions = []

        if self.countries:
            countries_str = ", ".join(f"'{c}'" for c in self.countries)
            conditions.append(f"country IN ({countries_str})")

        if self.roles:
            roles_str = ", ".join(f"'{r}'" for r in self.roles)
            conditions.append(f"role IN ({roles_str})")

        if self.data_sources:
            sources_str = ", ".join(f"'{s}'" for s in self.data_sources)
            conditions.append(f"data_source IN ({sources_str})")

        if not conditions:
            return None

        return " AND ".join(conditions)


class AnalyticsEngine:
    """Analytics engine for survey data using DuckDB."""

    def __init__(self, parquet_path: str, survey: SurveyDefinition | None = None):
        """Initialize the analytics engine.

        Args:
            parquet_path: Path to the Parquet file with survey responses
            survey: Survey definition (defaults to NCDN v1)
        """
        self.parquet_path = parquet_path
        self.survey = survey or load_ncdn_v1()
        self.con = duckdb.connect()

        # Create view for the data
        self.con.execute(f"""
            CREATE OR REPLACE VIEW survey_responses AS
            SELECT * FROM read_parquet('{parquet_path}')
        """)

    def get_summary_stats(
        self, filters: FilterCriteria | None = None
    ) -> dict[str, Any]:
        """Get high-level summary statistics.

        Args:
            filters: Optional filter criteria

        Returns:
            Dictionary with summary statistics
        """
        where_clause = filters.to_sql_where() if filters else None

        # Total unique respondents
        sql = "SELECT COUNT(DISTINCT respondent_id) FROM survey_responses"
        if where_clause:
            sql += f" WHERE {where_clause}"
        total_respondents = self.con.execute(sql).fetchone()[0]

        # By country
        sql = """
            SELECT country, data_source, COUNT(DISTINCT respondent_id) as count
            FROM survey_responses
        """
        if where_clause:
            sql += f" WHERE {where_clause}"
        sql += " GROUP BY country, data_source ORDER BY country"
        by_country = self.con.execute(sql).fetchdf().to_dict("records")

        # By role
        sql = """
            SELECT role, COUNT(DISTINCT respondent_id) as count
            FROM survey_responses
            WHERE role IS NOT NULL
        """
        if where_clause:
            sql += f" AND ({where_clause})"
        sql += " GROUP BY role ORDER BY count DESC"
        by_role = self.con.execute(sql).fetchdf().to_dict("records")

        return {
            "total_respondents": total_respondents,
            "by_country": by_country,
            "by_role": by_role,
        }

    def get_section_summary(
        self, section_id: str, filters: FilterCriteria | None = None
    ) -> pd.DataFrame:
        """Get summary for a survey section.

        Args:
            section_id: Section identifier
            filters: Optional filter criteria

        Returns:
            DataFrame with section summary
        """
        # Find section
        section = None
        for s in self.survey.sections:
            if s.section_id == section_id:
                section = s
                break

        if not section:
            raise ValueError(f"Section {section_id} not found")

        # Get question IDs in this section
        question_ids = [q.question_id for q in section.questions]
        questions_str = ", ".join(f"'{q}'" for q in question_ids)

        where_clause = filters.to_sql_where() if filters else None

        sql = f"""
            SELECT
                question_id,
                answer_type,
                answer_state,
                COUNT(*) as count,
                COUNT(DISTINCT respondent_id) as respondent_count
            FROM survey_responses
            WHERE question_id IN ({questions_str})
        """
        if where_clause:
            sql += f" AND ({where_clause})"
        sql += " GROUP BY question_id, answer_type, answer_state ORDER BY question_id"

        return self.con.execute(sql).fetchdf()

    def get_question_distribution(
        self,
        question_id: str,
        filters: FilterCriteria | None = None,
    ) -> pd.DataFrame:
        """Get answer distribution for a specific question.

        Args:
            question_id: Question identifier
            filters: Optional filter criteria

        Returns:
            DataFrame with answer distribution
        """
        where_clause = filters.to_sql_where() if filters else None

        sql = f"""
            SELECT
                answer_value,
                answer_state,
                COUNT(*) as count,
                COUNT(DISTINCT respondent_id) as respondent_count
            FROM survey_responses
            WHERE question_id = '{question_id}'
        """
        if where_clause:
            sql += f" AND ({where_clause})"
        sql += " GROUP BY answer_value, answer_state ORDER BY count DESC"

        return self.con.execute(sql).fetchdf()

    def get_multi_select_distribution(
        self,
        question_id: str,
        filters: FilterCriteria | None = None,
    ) -> pd.DataFrame:
        """Get distribution for multi-select question.

        Args:
            question_id: Question identifier
            filters: Optional filter criteria

        Returns:
            DataFrame with option frequencies
        """
        where_clause = filters.to_sql_where() if filters else None

        sql = f"""
            SELECT
                answer_value,
                COUNT(*) as count,
                COUNT(DISTINCT respondent_id) as respondent_count
            FROM survey_responses
            WHERE question_id = '{question_id}'
            AND answer_value IS NOT NULL
        """
        if where_clause:
            sql += f" AND ({where_clause})"
        sql += " GROUP BY answer_value ORDER BY count DESC"

        df = self.con.execute(sql).fetchdf()

        # Process multi-select values in Python
        option_counts = Counter()
        respondent_counts = Counter()

        for _, row in df.iterrows():
            options = row["answer_value"].split(",") if row["answer_value"] else []
            for opt in options:
                option_counts[opt] += row["count"]
                respondent_counts[opt] += row["respondent_count"]

        result_data = [
            {
                "option_id": opt,
                "count": option_counts[opt],
                "respondent_count": respondent_counts[opt],
            }
            for opt in option_counts
        ]
        result_data.sort(key=lambda x: x["count"], reverse=True)

        return pd.DataFrame(result_data)

    def get_ranking_distribution(
        self,
        question_id: str,
        filters: FilterCriteria | None = None,
    ) -> pd.DataFrame:
        """Get distribution for ranking question.

        Args:
            question_id: Question identifier
            filters: Optional filter criteria

        Returns:
            DataFrame with average rankings
        """
        where_clause = filters.to_sql_where() if filters else None

        sql = f"""
            SELECT
                answer_value,
                respondent_id
            FROM survey_responses
            WHERE question_id = '{question_id}'
            AND answer_value IS NOT NULL
        """
        if where_clause:
            sql += f" AND ({where_clause})"

        df = self.con.execute(sql).fetchdf()

        # Process rankings in Python
        rankings = defaultdict(list)

        for _, row in df.iterrows():
            options = row["answer_value"].split(",") if row["answer_value"] else []
            for rank, opt in enumerate(options, start=1):
                rankings[opt].append(rank)

        result_data = [
            {
                "option_id": opt,
                "average_rank": sum(ranks) / len(ranks),
                "count": len(ranks),
                "best_rank": min(ranks),
                "worst_rank": max(ranks),
            }
            for opt, ranks in rankings.items()
        ]
        result_data.sort(key=lambda x: x["average_rank"])

        return pd.DataFrame(result_data)

    def compare_countries(
        self,
        question_id: str,
        countries: list[str],
        filters: FilterCriteria | None = None,
    ) -> pd.DataFrame:
        """Compare responses across countries.

        Args:
            question_id: Question identifier
            countries: List of countries to compare
            filters: Optional filter criteria

        Returns:
            DataFrame with country comparison
        """
        countries_str = ", ".join(f"'{c}'" for c in countries)

        where_clause = filters.to_sql_where() if filters else None

        sql = f"""
            SELECT
                country,
                answer_value,
                COUNT(*) as count,
                COUNT(DISTINCT respondent_id) as respondent_count
            FROM survey_responses
            WHERE question_id = '{question_id}'
            AND country IN ({countries_str})
        """
        if where_clause:
            sql += f" AND ({where_clause})"
        sql += " GROUP BY country, answer_value ORDER BY country, count DESC"

        return self.con.execute(sql).fetchdf()

    def get_unique_values(self, column: str) -> list[str]:
        """Get unique values for a column.

        Args:
            column: Column name

        Returns:
            List of unique values
        """
        sql = f"""
            SELECT DISTINCT {column}
            FROM survey_responses
            WHERE {column} IS NOT NULL
            ORDER BY {column}
        """
        result = self.con.execute(sql).fetchall()
        return [row[0] for row in result]

    def get_text_responses(
        self,
        question_id: str,
        filters: FilterCriteria | None = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """Get text responses for a question.

        Args:
            question_id: Question identifier
            filters: Optional filter criteria
            limit: Maximum number of responses

        Returns:
            DataFrame with text responses
        """
        where_clause = filters.to_sql_where() if filters else None

        sql = f"""
            SELECT DISTINCT
                respondent_id,
                country,
                role,
                answer_value as text_response
            FROM survey_responses
            WHERE question_id = '{question_id}'
            AND answer_value IS NOT NULL
        """
        if where_clause:
            sql += f" AND ({where_clause})"
        sql += f" LIMIT {limit}"

        return self.con.execute(sql).fetchdf()

    def close(self) -> None:
        """Close the DuckDB connection."""
        self.con.close()

    def __enter__(self) -> "AnalyticsEngine":
        return self

    def __exit__(self, *args) -> None:
        self.close()
