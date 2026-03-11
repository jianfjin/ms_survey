import pytest

from ms_survey.definition.seed_ncdn_v1 import load_ncdn_v1
from ms_survey.responses.models import (
    AnswerState,
    CountryResponse,
    BooleanAnswer,
    MultiSelectAnswer,
)
from ms_survey.responses.validation import validate_country_response


def test_branch_followup_requires_true_trigger() -> None:
    definition = load_ncdn_v1()
    response = CountryResponse(
        country="Greece",
        answers=[
            BooleanAnswer(
                question_id="q_020_has_research_infra",
                state=AnswerState.ANSWERED,
                value=False,
            ),
            MultiSelectAnswer(
                question_id="q_021_research_infra_list",
                state=AnswerState.ANSWERED,
                option_ids=["infra_bbMRI"],
            ),
        ],
    )

    with pytest.raises(ValueError, match="branch rule"):
        validate_country_response(definition, response)


def test_branch_followup_allowed_when_trigger_true() -> None:
    definition = load_ncdn_v1()
    response = CountryResponse(
        country="Czech Republic",
        answers=[
            BooleanAnswer(
                question_id="q_020_has_research_infra",
                state=AnswerState.ANSWERED,
                value=True,
            ),
            MultiSelectAnswer(
                question_id="q_021_research_infra_list",
                state=AnswerState.ANSWERED,
                option_ids=["infra_bbMRI", "infra_eatris"],
            ),
        ],
    )

    validate_country_response(definition, response)
