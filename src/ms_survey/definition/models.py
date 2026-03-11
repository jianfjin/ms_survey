from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


QuestionType = Literal["single_select", "multi_select", "ranking", "text", "boolean"]


class OptionDefinition(BaseModel):
    option_id: str
    label: str


class BranchRule(BaseModel):
    source_question_id: str
    required_option_id: str | None = None
    required_boolean: bool | None = None


class QuestionDefinition(BaseModel):
    question_id: str
    display_number: int
    prompt: str
    question_type: QuestionType
    options: list[OptionDefinition] = Field(default_factory=list)
    branch_rules: list[BranchRule] = Field(default_factory=list)


class SectionDefinition(BaseModel):
    section_id: str
    title: str
    questions: list[QuestionDefinition]


class SurveyDefinition(BaseModel):
    survey_id: str
    version: str
    title: str
    sections: list[SectionDefinition]
