from __future__ import annotations

from ms_survey.definition.models import QuestionDefinition, SurveyDefinition
from ms_survey.responses.models import (
    BooleanAnswer,
    CountryResponse,
    MultiSelectAnswer,
    RankingAnswer,
    SingleSelectAnswer,
)


def _question_map(definition: SurveyDefinition) -> dict[str, QuestionDefinition]:
    return {
        question.question_id: question
        for section in definition.sections
        for question in section.questions
    }


def validate_country_response(
    definition: SurveyDefinition, response: CountryResponse
) -> None:
    questions_by_id: dict[str, QuestionDefinition] = _question_map(definition)
    answers_by_question_id = {answer.question_id: answer for answer in response.answers}

    for answer in response.answers:
        if answer.question_id not in questions_by_id:
            raise ValueError(f"unknown question id: {answer.question_id}")
        question = questions_by_id[answer.question_id]

        if answer.answer_type != question.question_type:
            raise ValueError(
                f"answer type mismatch for {answer.question_id}: expected {question.question_type}, got {answer.answer_type}"
            )

        if isinstance(answer, RankingAnswer):
            if len(set(answer.ranking)) != len(answer.ranking):
                raise ValueError("duplicate ranking option")

    for answer in response.answers:
        question = questions_by_id[answer.question_id]
        for branch_rule in question.branch_rules:
            source_answer = answers_by_question_id.get(branch_rule.source_question_id)
            if source_answer is None:
                raise ValueError(
                    f"branch rule violated for {answer.question_id}: missing trigger answer {branch_rule.source_question_id}"
                )

            if branch_rule.required_boolean is not None:
                if not isinstance(source_answer, BooleanAnswer):
                    raise ValueError(
                        f"branch rule violated for {answer.question_id}: trigger is not boolean"
                    )
                if source_answer.value != branch_rule.required_boolean:
                    raise ValueError(
                        f"branch rule violated for {answer.question_id}: expected trigger {branch_rule.source_question_id}={branch_rule.required_boolean}"
                    )

            if branch_rule.required_option_id is not None:
                if isinstance(source_answer, SingleSelectAnswer):
                    valid = source_answer.option_id == branch_rule.required_option_id
                elif isinstance(source_answer, MultiSelectAnswer):
                    valid = branch_rule.required_option_id in source_answer.option_ids
                else:
                    valid = False

                if not valid:
                    raise ValueError(
                        f"branch rule violated for {answer.question_id}: required option {branch_rule.required_option_id}"
                    )
