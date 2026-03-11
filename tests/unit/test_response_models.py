import pytest

from ms_survey.definition.seed_ncdn_v1 import load_ncdn_v1
from ms_survey.responses.models import (
    AnswerState,
    CountryResponse,
    MultiSelectAnswer,
    RankingAnswer,
    SingleSelectAnswer,
    TextAnswer,
)
from ms_survey.responses.validation import validate_country_response


def test_valid_country_response_passes_definition_validation() -> None:
    definition = load_ncdn_v1()
    response = CountryResponse(
        country="Greece",
        answers=[
            TextAnswer(
                question_id="q_001_respondent_name",
                state=AnswerState.ANSWERED,
                text="Anon",
            ),
            MultiSelectAnswer(
                question_id="q_007_stakeholder_views",
                state=AnswerState.ANSWERED,
                option_ids=["stakeholder_patients", "stakeholder_researchers"],
            ),
            RankingAnswer(
                question_id="q_010_function_ranking",
                state=AnswerState.ANSWERED,
                ranking=[
                    "fn_common_variables",
                    "fn_data_quality",
                    "fn_metadata",
                    "fn_tools_spe",
                ],
            ),
            SingleSelectAnswer(
                question_id="q_077_has_national_strategy",
                state=AnswerState.ANSWERED,
                option_id="yes",
            ),
        ],
    )

    validate_country_response(definition, response)


def test_duplicate_ranking_entries_are_rejected() -> None:
    definition = load_ncdn_v1()
    response = CountryResponse(
        country="Czech Republic",
        answers=[
            RankingAnswer(
                question_id="q_010_function_ranking",
                state=AnswerState.ANSWERED,
                ranking=[
                    "fn_common_variables",
                    "fn_common_variables",
                    "fn_metadata",
                    "fn_tools_spe",
                ],
            )
        ],
    )

    with pytest.raises(ValueError, match="duplicate ranking option"):
        validate_country_response(definition, response)
