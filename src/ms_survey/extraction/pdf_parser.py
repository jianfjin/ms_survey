"""PDF extraction module for survey responses.

Note: The PDFs appear to be scanned images. This module provides:
1. OCR-based extraction (requires tesseract)
2. Manual transcription helpers for data entry
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from ms_survey.definition.seed_ncdn_v1 import load_ncdn_v1
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


def extract_pdf_with_ocr(pdf_path: str) -> dict[str, Any]:
    """Extract survey data from PDF using OCR.

    Requires tesseract-ocr to be installed on the system.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Dictionary with extracted response data

    Raises:
        RuntimeError: If OCR dependencies are not available
    """
    try:
        import pytesseract
        from pdf2image import convert_from_path
    except ImportError as e:
        raise RuntimeError(
            "OCR dependencies not installed. "
            "Install with: uv pip install pdf2image pytesseract"
        ) from e

    try:
        pytesseract.get_tesseract_version()
    except Exception as e:
        raise RuntimeError(
            "Tesseract OCR not found. Please install tesseract-ocr: "
            "https://github.com/UB-Mannheim/tesseract/wiki"
        ) from e

    images = convert_from_path(pdf_path)
    full_text = ""
    for image in images:
        text = pytesseract.image_to_string(image)
        full_text += text + "\n"

    return {"raw_text": full_text, "pages": len(images)}


def create_transcription_template(output_path: str) -> None:
    """Create a JSON template for manual data entry from PDFs.

    Since the PDFs are scanned images, this template helps manually
    transcribe the responses into structured format.

    Args:
        output_path: Path to write the template JSON file
    """
    survey = load_ncdn_v1()

    template = {
        "template_version": "1.0",
        "survey_id": survey.survey_id,
        "survey_version": survey.version,
        "instructions": (
            "Fill in the response data from the PDF survey. "
            "For each question, provide the answer value. "
            "Leave blank for unanswered questions."
        ),
        "respondent_metadata": {
            "country": "",  # e.g., "Greece", "Czech Republic"
            "respondent_name": "",
            "respondent_email": "",
            "role": "",  # e.g., "Researcher", "Clinician", "Policy Maker"
            "organization": "",
        },
        "questions": [],
    }

    for section in survey.sections:
        for question in section.questions:
            q_template = {
                "question_id": question.question_id,
                "display_number": question.display_number,
                "section": section.title,
                "prompt": question.prompt,
                "question_type": question.question_type,
                "answer": None,
            }
            if question.options:
                q_template["options"] = [
                    {"option_id": opt.option_id, "label": opt.label}
                    for opt in question.options
                ]
            template["questions"].append(q_template)

    Path(output_path).write_text(
        json.dumps(template, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def parse_transcription_file(json_path: str) -> CountryResponse:
    """Parse a filled transcription template into a CountryResponse.

    Args:
        json_path: Path to the filled transcription JSON file

    Returns:
        CountryResponse object
    """
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))

    metadata = RespondentMetadata(
        respondent_name=data["respondent_metadata"].get("respondent_name") or None,
        respondent_email=data["respondent_metadata"].get("respondent_email") or None,
        role=data["respondent_metadata"].get("role") or None,
        organization=data["respondent_metadata"].get("organization") or None,
    )

    answers: list[Answer] = []
    for q in data["questions"]:
        answer = _parse_question_answer(q)
        if answer:
            answers.append(answer)

    return CountryResponse(
        country=data["respondent_metadata"]["country"],
        metadata=metadata,
        answers=answers,
    )


def _parse_question_answer(q: dict[str, Any]) -> Answer | None:
    """Parse a single question answer from transcription data."""
    q_id = q["question_id"]
    q_type = q["question_type"]
    answer_value = q.get("answer")

    # Handle blank/unanswered
    if answer_value is None or answer_value == "":
        return _create_blank_answer(q_id, q_type)

    if q_type == "single_select":
        return SingleSelectAnswer(
            question_id=q_id,
            state=AnswerState.ANSWERED,
            option_id=str(answer_value),
        )
    elif q_type == "multi_select":
        if isinstance(answer_value, list):
            option_ids = [str(v) for v in answer_value]
        else:
            option_ids = [str(answer_value)]
        return MultiSelectAnswer(
            question_id=q_id,
            state=AnswerState.ANSWERED,
            option_ids=option_ids,
        )
    elif q_type == "ranking":
        if isinstance(answer_value, list):
            ranking = [str(v) for v in answer_value]
        else:
            ranking = []
        return RankingAnswer(
            question_id=q_id,
            state=AnswerState.ANSWERED if ranking else AnswerState.BLANK,
            ranking=ranking,
        )
    elif q_type == "text":
        return TextAnswer(
            question_id=q_id,
            state=AnswerState.ANSWERED,
            text=str(answer_value),
        )
    elif q_type == "boolean":
        if isinstance(answer_value, bool):
            value = answer_value
        else:
            value = str(answer_value).lower() in ("true", "yes", "1", "t")
        return BooleanAnswer(
            question_id=q_id,
            state=AnswerState.ANSWERED,
            value=value,
        )

    return None


def _create_blank_answer(question_id: str, question_type: str) -> Answer:
    """Create a blank answer for the given question type."""
    if question_type == "single_select":
        return SingleSelectAnswer(
            question_id=question_id,
            state=AnswerState.BLANK,
            option_id=None,
        )
    elif question_type == "multi_select":
        return MultiSelectAnswer(
            question_id=question_id,
            state=AnswerState.BLANK,
            option_ids=[],
        )
    elif question_type == "ranking":
        return RankingAnswer(
            question_id=question_id,
            state=AnswerState.BLANK,
            ranking=[],
        )
    elif question_type == "text":
        return TextAnswer(
            question_id=question_id,
            state=AnswerState.BLANK,
            text=None,
        )
    elif question_type == "boolean":
        return BooleanAnswer(
            question_id=question_id,
            state=AnswerState.BLANK,
            value=None,
        )
    else:
        return TextAnswer(
            question_id=question_id,
            state=AnswerState.BLANK,
            text=None,
        )
