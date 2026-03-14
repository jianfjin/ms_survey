"""Synthetic data generator for survey responses."""

from __future__ import annotations

import random
import uuid
from datetime import datetime
from typing import Any

from ms_survey.definition.seed_ncdn_v1 import load_ncdn_v1
from ms_survey.definition.models import QuestionDefinition, SurveyDefinition
from ms_survey.responses.models import (
    Answer,
    AnswerState,
    BooleanAnswer,
    CountryResponse,
    MultiSelectAnswer,
    RankingAnswer,
    RespondentMetadata,
    SingleSelectAnswer,
    TextAnswer,
)


# Realistic metadata distributions
COUNTRIES = ["Greece", "Czech Republic", "Italy", "Spain", "Poland"]

ROLES = [
    "Researcher",
    "Clinician",
    "Data Manager",
    "Policy Maker",
    "Healthcare Administrator",
    "IT Specialist",
    "Patient Advocate",
]

STAKEHOLDER_GROUPS = [
    "stakeholder_patients",
    "stakeholder_clinicians",
    "stakeholder_researchers",
    "stakeholder_policy_makers",
]

ORGANIZATIONS = [
    "National Cancer Institute",
    "University Hospital",
    "Ministry of Health",
    "Research Foundation",
    "Cancer Registry",
    "Healthcare IT Department",
    "Patient Organization",
    "Medical University",
]

# Country-specific response patterns (for realistic synthetic data)
COUNTRY_PATTERNS = {
    "Greece": {
        "has_research_infra": 0.7,  # 70% say yes
        "has_national_strategy": 0.4,
        "common_stakeholders": ["stakeholder_clinicians", "stakeholder_researchers"],
    },
    "Czech Republic": {
        "has_research_infra": 0.8,
        "has_national_strategy": 0.6,
        "common_stakeholders": ["stakeholder_researchers", "stakeholder_policy_makers"],
    },
}


class SyntheticDataGenerator:
    """Generate realistic synthetic survey responses."""
    
    def __init__(self, survey: SurveyDefinition | None = None, seed: int | None = None):
        """Initialize the generator.
        
        Args:
            survey: Survey definition (defaults to NCDN v1)
            seed: Random seed for reproducibility
        """
        self.survey = survey or load_ncdn_v1()
        self.rng = random.Random(seed)
    
    def generate_respondents(
        self,
        countries: list[str],
        count_per_country: int = 100,
    ) -> list[CountryResponse]:
        """Generate synthetic respondents for specified countries.
        
        Args:
            countries: List of country names
            count_per_country: Number of respondents per country
            
        Returns:
            List of CountryResponse objects
        """
        responses = []
        for country in countries:
            for _ in range(count_per_country):
                response = self._generate_single_respondent(country)
                responses.append(response)
        return responses
    
    def _generate_single_respondent(self, country: str) -> CountryResponse:
        """Generate a single synthetic respondent."""
        # Generate metadata
        role = self.rng.choice(ROLES)
        metadata = RespondentMetadata(
            respondent_name=f"Respondent_{uuid.uuid4().hex[:8]}",
            respondent_email=None,  # Keep private
            role=role,
            organization=self.rng.choice(ORGANIZATIONS),
        )
        
        # Generate answers for all questions
        answers = []
        for section in self.survey.sections:
            for question in section.questions:
                answer = self._generate_answer(question, country, role)
                if answer:
                    answers.append(answer)
        
        return CountryResponse(
            country=country,
            metadata=metadata,
            answers=answers,
        )
    
    def _generate_answer(
        self,
        question: QuestionDefinition,
        country: str,
        role: str,
    ) -> Answer | None:
        """Generate an answer for a specific question."""
        q_type = question.question_type
        q_id = question.question_id
        
        # Check branching rules - skip if conditions not met
        # For synthetic data, we simulate the branching logic
        if self._should_skip_question(q_id, country):
            return self._create_blank_answer(q_id, q_type)
        
        # Generate answer based on type
        if q_type == "single_select":
            return self._generate_single_select_answer(question, country)
        elif q_type == "multi_select":
            return self._generate_multi_select_answer(question, country, role)
        elif q_type == "ranking":
            return self._generate_ranking_answer(question)
        elif q_type == "text":
            return self._generate_text_answer(question, country)
        elif q_type == "boolean":
            return self._generate_boolean_answer(question, country)
        
        return None
    
    def _should_skip_question(self, question_id: str, country: str) -> bool:
        """Determine if a question should be skipped based on branching."""
        # Simulate branching logic
        # Q21 (research_infra_list) only if Q20 (has_research_infra) is True
        if question_id == "q_021_research_infra_list":
            pattern = COUNTRY_PATTERNS.get(country, {})
            prob = pattern.get("has_research_infra", 0.5)
            return not (self.rng.random() < prob)
        return False
    
    def _generate_single_select_answer(
        self,
        question: QuestionDefinition,
        country: str,
    ) -> SingleSelectAnswer:
        """Generate a single select answer."""
        # Apply country-specific patterns for certain questions
        if question.question_id == "q_077_has_national_strategy":
            pattern = COUNTRY_PATTERNS.get(country, {})
            prob_yes = pattern.get("has_national_strategy", 0.5)
            option_id = "yes" if self.rng.random() < prob_yes else "no"
        elif question.question_id == "q_020_has_research_infra":
            pattern = COUNTRY_PATTERNS.get(country, {})
            prob_yes = pattern.get("has_research_infra", 0.5)
            option_id = "yes" if self.rng.random() < prob_yes else "no"
        else:
            # Random selection from options
            if question.options:
                option = self.rng.choice(question.options)
                option_id = option.option_id
            else:
                option_id = "unknown"
        
        return SingleSelectAnswer(
            question_id=question.question_id,
            state=AnswerState.ANSWERED,
            option_id=option_id,
        )
    
    def _generate_multi_select_answer(
        self,
        question: QuestionDefinition,
        country: str,
        role: str,
    ) -> MultiSelectAnswer:
        """Generate a multi-select answer."""
        if not question.options:
            return MultiSelectAnswer(
                question_id=question.question_id,
                state=AnswerState.ANSWERED,
                option_ids=[],
            )
        
        # Special handling for stakeholder question
        if question.question_id == "q_007_stakeholder_views":
            pattern = COUNTRY_PATTERNS.get(country, {})
            common = pattern.get("common_stakeholders", [])
            
            # Always include role-appropriate stakeholders
            option_ids = list(common)
            if role in ["Clinician", "Healthcare Administrator"]:
                if "stakeholder_clinicians" not in option_ids:
                    option_ids.append("stakeholder_clinicians")
            if role in ["Researcher", "Data Manager"]:
                if "stakeholder_researchers" not in option_ids:
                    option_ids.append("stakeholder_researchers")
            if role == "Policy Maker":
                if "stakeholder_policy_makers" not in option_ids:
                    option_ids.append("stakeholder_policy_makers")
            
            # Add 1-2 random additional stakeholders
            available = [opt.option_id for opt in question.options if opt.option_id not in option_ids]
            if available:
                extra_count = min(self.rng.randint(1, 2), len(available))
                option_ids.extend(self.rng.sample(available, extra_count))
        else:
            # Random selection of 1-3 options
            count = min(self.rng.randint(1, 3), len(question.options))
            selected = self.rng.sample(question.options, count)
            option_ids = [opt.option_id for opt in selected]
        
        return MultiSelectAnswer(
            question_id=question.question_id,
            state=AnswerState.ANSWERED,
            option_ids=option_ids,
        )
    
    def _generate_ranking_answer(self, question: QuestionDefinition) -> RankingAnswer:
        """Generate a ranking answer."""
        if not question.options:
            return RankingAnswer(
                question_id=question.question_id,
                state=AnswerState.ANSWERED,
                ranking=[],
            )
        
        # Shuffle all options to create a ranking
        option_ids = [opt.option_id for opt in question.options]
        self.rng.shuffle(option_ids)
        
        return RankingAnswer(
            question_id=question.question_id,
            state=AnswerState.ANSWERED,
            ranking=option_ids,
        )
    
    def _generate_text_answer(
        self,
        question: QuestionDefinition,
        country: str,
    ) -> TextAnswer:
        """Generate a text answer."""
        # Generate realistic text responses based on question
        text = ""
        if "name" in question.question_id:
            text = f"Respondent from {country}"
        elif "project" in question.question_id.lower() or "initiative" in question.prompt.lower():
            projects = [
                f"National Cancer Registry {country}",
                "EUPROCAT collaboration",
                "EUROCARE data linkage project",
                "Local hospital quality initiative",
                "Not applicable",
            ]
            text = self.rng.choice(projects)
        elif "considerations" in question.question_id.lower() or "establishment" in question.prompt.lower():
            considerations = [
                "Data privacy and GDPR compliance; Interoperability with existing systems; Funding sustainability",
                "Stakeholder engagement; Technical infrastructure; Legal framework alignment",
                "Quality assurance processes; Training for staff; International standards adoption",
                "Integration with clinical workflows; Patient consent mechanisms; Long-term governance",
            ]
            text = self.rng.choice(considerations)
        else:
            text = f"Response from {country} - detailed feedback provided"
        
        return TextAnswer(
            question_id=question.question_id,
            state=AnswerState.ANSWERED,
            text=text,
        )
    
    def _generate_boolean_answer(
        self,
        question: QuestionDefinition,
        country: str,
    ) -> BooleanAnswer:
        """Generate a boolean answer."""
        # Apply country patterns where relevant
        if question.question_id == "q_020_has_research_infra":
            pattern = COUNTRY_PATTERNS.get(country, {})
            prob = pattern.get("has_research_infra", 0.5)
            value = self.rng.random() < prob
        else:
            value = self.rng.choice([True, False])
        
        return BooleanAnswer(
            question_id=question.question_id,
            state=AnswerState.ANSWERED,
            value=value,
        )
    
    def _create_blank_answer(self, question_id: str, question_type: str) -> Answer:
        """Create a blank/skipped answer."""
        if question_type == "single_select":
            return SingleSelectAnswer(
                question_id=question_id,
                state=AnswerState.NOT_APPLICABLE,
                option_id=None,
            )
        elif question_type == "multi_select":
            return MultiSelectAnswer(
                question_id=question_id,
                state=AnswerState.NOT_APPLICABLE,
                option_ids=[],
            )
        elif question_type == "ranking":
            return RankingAnswer(
                question_id=question_id,
                state=AnswerState.NOT_APPLICABLE,
                ranking=[],
            )
        elif question_type == "text":
            return TextAnswer(
                question_id=question_id,
                state=AnswerState.NOT_APPLICABLE,
                text=None,
            )
        elif question_type == "boolean":
            return BooleanAnswer(
                question_id=question_id,
                state=AnswerState.NOT_APPLICABLE,
                value=None,
            )
        else:
            return TextAnswer(
                question_id=question_id,
                state=AnswerState.NOT_APPLICABLE,
                text=None,
            )


def generate_synthetic_dataset(
    countries: list[str],
    count_per_country: int = 100,
    seed: int = 42,
) -> list[CountryResponse]:
    """Convenience function to generate synthetic dataset.
    
    Args:
        countries: List of country names
        count_per_country: Number of respondents per country
        seed: Random seed for reproducibility
        
    Returns:
        List of CountryResponse objects
    """
    generator = SyntheticDataGenerator(seed=seed)
    return generator.generate_respondents(countries, count_per_country)
