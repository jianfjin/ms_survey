from ms_survey.definition.models import (
    BranchRule,
    OptionDefinition,
    QuestionDefinition,
    SectionDefinition,
    SurveyDefinition,
)


def load_ncdn_v1() -> SurveyDefinition:
    return SurveyDefinition(
        survey_id="ncdn",
        version="v1",
        title="National Cancer Data Node Questionnaire",
        sections=[
            SectionDefinition(
                section_id="section_1_general_info",
                title="General Information",
                questions=[
                    QuestionDefinition(
                        question_id="q_001_respondent_name",
                        display_number=1,
                        prompt="Respondent's name",
                        question_type="text",
                    ),
                    QuestionDefinition(
                        question_id="q_007_stakeholder_views",
                        display_number=7,
                        prompt="Which stakeholder groups views are you familiar with?",
                        question_type="multi_select",
                        options=[
                            OptionDefinition(
                                option_id="stakeholder_patients", label="Patients"
                            ),
                            OptionDefinition(
                                option_id="stakeholder_clinicians", label="Clinicians"
                            ),
                            OptionDefinition(
                                option_id="stakeholder_researchers", label="Researchers"
                            ),
                            OptionDefinition(
                                option_id="stakeholder_policy_makers",
                                label="Policy makers",
                            ),
                        ],
                    ),
                    QuestionDefinition(
                        question_id="q_010_function_ranking",
                        display_number=10,
                        prompt="Rank functions 2-5 by relevance",
                        question_type="ranking",
                        options=[
                            OptionDefinition(
                                option_id="fn_data_quality",
                                label="Improve data quality",
                            ),
                            OptionDefinition(
                                option_id="fn_metadata", label="Metadata record"
                            ),
                            OptionDefinition(
                                option_id="fn_common_variables",
                                label="Common variables",
                            ),
                            OptionDefinition(
                                option_id="fn_tools_spe",
                                label="Tools for analysis in SPE",
                            ),
                        ],
                    ),
                ],
            ),
            SectionDefinition(
                section_id="section_2_functions",
                title="NCDN Functions",
                questions=[
                    QuestionDefinition(
                        question_id="q_020_has_research_infra",
                        display_number=20,
                        prompt="Are there infrastructures supporting cancer data holders?",
                        question_type="boolean",
                    ),
                    QuestionDefinition(
                        question_id="q_021_research_infra_list",
                        display_number=21,
                        prompt="What infrastructures exist in your country?",
                        question_type="multi_select",
                        branch_rules=[
                            BranchRule(
                                source_question_id="q_020_has_research_infra",
                                required_boolean=True,
                            )
                        ],
                        options=[
                            OptionDefinition(
                                option_id="infra_bbMRI", label="BBMRI-ERIC"
                            ),
                            OptionDefinition(option_id="infra_elixir", label="ELIXIR"),
                            OptionDefinition(
                                option_id="infra_eatris", label="EATRIS-ERIC"
                            ),
                        ],
                    ),
                    QuestionDefinition(
                        question_id="q_031_clinical_data_quality_projects",
                        display_number=31,
                        prompt="Please name initiatives/projects for clinical data quality",
                        question_type="text",
                    ),
                ],
            ),
            SectionDefinition(
                section_id="section_3_operations",
                title="NCDN Operations",
                questions=[
                    QuestionDefinition(
                        question_id="q_077_has_national_strategy",
                        display_number=77,
                        prompt="Does your country have a national cancer data strategy?",
                        question_type="single_select",
                        options=[
                            OptionDefinition(option_id="yes", label="Yes"),
                            OptionDefinition(option_id="no", label="No"),
                            OptionDefinition(option_id="unknown", label="I don't know"),
                        ],
                    ),
                    QuestionDefinition(
                        question_id="q_082_establishment_considerations",
                        display_number=82,
                        prompt="What are your key considerations for NCDN establishment?",
                        question_type="text",
                    ),
                ],
            ),
        ],
    )
