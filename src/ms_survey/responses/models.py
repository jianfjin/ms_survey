from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator


class AnswerState(StrEnum):
    ANSWERED = "answered"
    BLANK = "blank"
    SKIPPED = "skipped"
    NOT_APPLICABLE = "not_applicable"


class AnswerBase(BaseModel):
    question_id: str
    state: AnswerState


class SingleSelectAnswer(AnswerBase):
    answer_type: Literal["single_select"] = "single_select"
    option_id: str | None = None

    @model_validator(mode="after")
    def validate_state_and_option(self) -> "SingleSelectAnswer":
        if self.state == AnswerState.ANSWERED and not self.option_id:
            raise ValueError("answered single_select requires option_id")
        if self.state != AnswerState.ANSWERED and self.option_id is not None:
            raise ValueError("non-answered single_select must not include option_id")
        return self


class MultiSelectAnswer(AnswerBase):
    answer_type: Literal["multi_select"] = "multi_select"
    option_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_state_and_options(self) -> "MultiSelectAnswer":
        if self.state == AnswerState.ANSWERED and not self.option_ids:
            raise ValueError("answered multi_select requires option_ids")
        if self.state != AnswerState.ANSWERED and self.option_ids:
            raise ValueError("non-answered multi_select must have empty option_ids")
        return self


class RankingAnswer(AnswerBase):
    answer_type: Literal["ranking"] = "ranking"
    ranking: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_state_and_ranking(self) -> "RankingAnswer":
        if self.state == AnswerState.ANSWERED and not self.ranking:
            raise ValueError("answered ranking requires ranking values")
        if self.state != AnswerState.ANSWERED and self.ranking:
            raise ValueError("non-answered ranking must have empty values")
        return self


class TextAnswer(AnswerBase):
    answer_type: Literal["text"] = "text"
    text: str | None = None

    @model_validator(mode="after")
    def validate_state_and_text(self) -> "TextAnswer":
        if self.state == AnswerState.ANSWERED and (
            self.text is None or self.text == ""
        ):
            raise ValueError("answered text requires non-empty text")
        if self.state != AnswerState.ANSWERED and self.text is not None:
            raise ValueError("non-answered text must not include text")
        return self


class BooleanAnswer(AnswerBase):
    answer_type: Literal["boolean"] = "boolean"
    value: bool | None = None

    @model_validator(mode="after")
    def validate_state_and_value(self) -> "BooleanAnswer":
        if self.state == AnswerState.ANSWERED and self.value is None:
            raise ValueError("answered boolean requires value")
        if self.state != AnswerState.ANSWERED and self.value is not None:
            raise ValueError("non-answered boolean must not include value")
        return self


Answer = Annotated[
    SingleSelectAnswer | MultiSelectAnswer | RankingAnswer | TextAnswer | BooleanAnswer,
    Field(discriminator="answer_type"),
]


class RespondentMetadata(BaseModel):
    respondent_name: str | None = None
    respondent_email: str | None = None
    role: str | None = None
    organization: str | None = None


class CountryResponse(BaseModel):
    country: str
    metadata: RespondentMetadata | None = None
    answers: list[Answer]
