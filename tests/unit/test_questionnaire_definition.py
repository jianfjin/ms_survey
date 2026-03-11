from ms_survey.definition.seed_ncdn_v1 import load_ncdn_v1


def test_load_ncdn_v1_has_expected_sections_and_types() -> None:
    definition = load_ncdn_v1()

    assert definition.survey_id == "ncdn"
    assert definition.version == "v1"
    assert [section.section_id for section in definition.sections] == [
        "section_1_general_info",
        "section_2_functions",
        "section_3_operations",
    ]

    observed_types = {
        question.question_type
        for section in definition.sections
        for question in section.questions
    }
    assert {"single_select", "multi_select", "ranking", "text", "boolean"}.issubset(
        observed_types
    )


def test_stable_question_ids_are_separate_from_display_numbers() -> None:
    definition = load_ncdn_v1()
    first_question = definition.sections[0].questions[0]

    assert first_question.question_id.startswith("q_")
    assert first_question.display_number == 1
    assert first_question.question_id != str(first_question.display_number)
