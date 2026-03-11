from ms_survey.responses.models import AnswerState, MultiSelectAnswer, TextAnswer


def test_blank_skipped_and_not_applicable_are_distinct_states() -> None:
    blank = TextAnswer(
        question_id="q_031_clinical_data_quality_projects",
        state=AnswerState.BLANK,
        text=None,
    )
    skipped = TextAnswer(
        question_id="q_031_clinical_data_quality_projects",
        state=AnswerState.SKIPPED,
        text=None,
    )
    not_applicable = MultiSelectAnswer(
        question_id="q_021_research_infra_list",
        state=AnswerState.NOT_APPLICABLE,
        option_ids=[],
    )

    assert blank.state != skipped.state
    assert skipped.state != not_applicable.state
    assert blank.state != not_applicable.state
