"""Parse the CANDLE NCDN Excel workbook into normalized data frames."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

import pandas as pd

from ms_survey.privacy import mask_text_balanced

_NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
}

_SYSTEM_COLUMNS = {
    "ID",
    "Alkamisaika",
    "Valmistumisaika",
    "Sähköposti",
    "Nimi",
    "Kieli",
    "Edellinen muokkausaika",
    "Respondent's name",
    "Respondent's email",
}

_COUNTRY_TO_ISO = {
    "ALBANIA": "AL",
    "AUSTRIA": "AT",
    "BELGIUM": "BE",
    "BULGARIA": "BG",
    "CROATIA": "HR",
    "CYPRUS": "CY",
    "CZECH REPUBLIC": "CZ",
    "CZECHIA": "CZ",
    "DENMARK": "DK",
    "ESTONIA": "EE",
    "FINLAND": "FI",
    "FRANCE": "FR",
    "GERMANY": "DE",
    "GREECE": "GR",
    "HUNGARY": "HU",
    "ICELAND": "IS",
    "IRELAND": "IE",
    "ITALY": "IT",
    "LATVIA": "LV",
    "LITHUANIA": "LT",
    "LUXEMBOURG": "LU",
    "MALTA": "MT",
    "NETHERLANDS": "NL",
    "THE NETHERLANDS": "NL",
    "NORWAY": "NO",
    "POLAND": "PL",
    "PORTUGAL": "PT",
    "ROMANIA": "RO",
    "SLOVAKIA": "SK",
    "SLOVENIA": "SI",
    "SPAIN": "ES",
    "SWEDEN": "SE",
    "SWITZERLAND": "CH",
    "UNITED KINGDOM": "GB",
    "UK": "GB",
}

_MISSING_MARKERS = {"", "-", "n/a", "na", "none", "null", "i dont know", "i don't know"}


@dataclass
class ParsedWorkbook:
    respondents: pd.DataFrame
    questions: pd.DataFrame
    answers: pd.DataFrame


def parse_excel_workbook(path: str | Path) -> ParsedWorkbook:
    """Parse workbook into respondents, questions, and masked answers tables."""
    workbook_path = Path(path)
    if not workbook_path.exists():
        raise FileNotFoundError(f"Workbook not found: {workbook_path}")

    raw_df = _read_first_sheet(workbook_path)
    if raw_df.empty:
        raise ValueError("Workbook contains no rows")

    raw_df = raw_df.rename(columns=lambda value: str(value).strip())
    raw_df = raw_df.fillna("")

    country_col = _find_column(raw_df.columns, "Country of the respondent")
    role_col = _find_column(raw_df.columns, "In what role are you representing your country?")
    org_col = _find_column(raw_df.columns, "Organization of the respondent")
    stakeholder_col = _find_column(
        raw_df.columns, "Which stakeholder groups views are you familiar with?"
    )

    respondent_rows: list[dict[str, str]] = []
    answer_rows: list[dict[str, str | int]] = []
    question_rows: list[dict[str, str | int]] = []

    question_columns = _get_question_columns(raw_df.columns)
    question_map: dict[str, dict[str, str | int]] = {}
    for idx, column in enumerate(question_columns, start=1):
        prompt = _normalize_spaces(column)
        question_id = f"q_{idx:03d}"
        section_id = _infer_section_id(prompt)
        question_type = _infer_question_type(prompt=prompt, value="")
        question_map[column] = {
            "question_id": question_id,
            "question_prompt": prompt,
            "section_id": section_id,
            "question_order": idx,
            "question_type": question_type,
        }
        question_rows.append(
            {
                "question_id": question_id,
                "question_prompt": prompt,
                "section_id": section_id,
                "question_order": idx,
                "question_type": question_type,
            }
        )

    for row_number, row in raw_df.iterrows():
        country_name = _normalize_spaces(str(row.get(country_col, "")))
        if not country_name:
            # Skip blank respondent rows.
            continue

        respondent_id = f"resp_{row_number + 1:03d}"
        country_iso = country_name_to_iso(country_name)
        respondent_rows.append(
            {
                "respondent_id": respondent_id,
                "country_name": country_name,
                "country_iso": country_iso,
                "role": _normalize_spaces(str(row.get(role_col, ""))) or None,
                "organization": _normalize_spaces(str(row.get(org_col, ""))) or None,
                "stakeholder_groups": _normalize_spaces(
                    str(row.get(stakeholder_col, ""))
                )
                or None,
                "data_source": "original_excel",
            }
        )

        for column in question_columns:
            question_info = question_map[column]
            raw_value = _normalize_spaces(str(row.get(column, "")))
            answer_state = "blank" if _is_missing(raw_value) else "answered"
            question_type = str(question_info["question_type"])
            if answer_state == "answered":
                if ";" in raw_value and question_type != "ranking":
                    question_type = "multi_select"
                elif raw_value.lower() in {"yes", "no", "true", "false"}:
                    question_type = "boolean"

            answer_rows.append(
                {
                    "respondent_id": respondent_id,
                    "country_iso": country_iso,
                    "section_id": question_info["section_id"],
                    "question_id": question_info["question_id"],
                    "question_prompt": question_info["question_prompt"],
                    "question_order": question_info["question_order"],
                    "question_type": question_type,
                    "answer_state": answer_state,
                    "answer_value_masked": _normalize_answer_value(
                        value=raw_value,
                        question_type=question_type,
                        answer_state=answer_state,
                    ),
                }
            )

    respondents = pd.DataFrame(respondent_rows)
    questions = pd.DataFrame(question_rows)
    answers = pd.DataFrame(answer_rows)

    if not answers.empty:
        answers = answers.sort_values(
            ["question_order", "country_iso", "respondent_id"], ascending=True
        ).reset_index(drop=True)

    return ParsedWorkbook(
        respondents=respondents.reset_index(drop=True),
        questions=questions.reset_index(drop=True),
        answers=answers,
    )


def country_name_to_iso(country_name: str) -> str:
    """Convert country name to ISO alpha-2 (best effort)."""
    normalized = _normalize_country_key(country_name)
    if normalized in _COUNTRY_TO_ISO:
        return _COUNTRY_TO_ISO[normalized]

    if re.fullmatch(r"[A-Za-z]{2}", country_name.strip()):
        return country_name.strip().upper()

    return "UNK"


def _read_first_sheet(path: Path) -> pd.DataFrame:
    with zipfile.ZipFile(path) as zip_file:
        workbook = ET.fromstring(zip_file.read("xl/workbook.xml"))
        rels = ET.fromstring(zip_file.read("xl/_rels/workbook.xml.rels"))
        rel_targets = {
            relation.attrib["Id"]: relation.attrib["Target"]
            for relation in rels.findall("pr:Relationship", _NS)
        }

        first_sheet = workbook.find("a:sheets/a:sheet", _NS)
        if first_sheet is None:
            return pd.DataFrame()

        rel_id = first_sheet.attrib.get(
            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
        )
        if rel_id is None or rel_id not in rel_targets:
            return pd.DataFrame()

        target = rel_targets[rel_id].replace("\\", "/")
        sheet_path = f"xl/{target.lstrip('/')}"

        shared_strings = _read_shared_strings(zip_file)
        sheet_xml = ET.fromstring(zip_file.read(sheet_path))
        rows = sheet_xml.findall(".//a:sheetData/a:row", _NS)
        if not rows:
            return pd.DataFrame()

        header_cells = _read_row_values(rows[0], shared_strings)
        headers_by_index = {
            column_index: _normalize_spaces(value)
            for column_index, value in header_cells.items()
            if value
        }
        if not headers_by_index:
            return pd.DataFrame()

        ordered_columns = [
            headers_by_index[index] for index in sorted(headers_by_index.keys())
        ]
        records: list[dict[str, str]] = []
        for row in rows[1:]:
            values = _read_row_values(row, shared_strings)
            record: dict[str, str] = {}
            for index, column_name in zip(sorted(headers_by_index.keys()), ordered_columns):
                record[column_name] = values.get(index, "")
            records.append(record)

        return pd.DataFrame(records)


def _read_shared_strings(zip_file: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in zip_file.namelist():
        return []

    shared_strings_xml = ET.fromstring(zip_file.read("xl/sharedStrings.xml"))
    strings: list[str] = []
    for string_item in shared_strings_xml.findall("a:si", _NS):
        text = "".join(node.text or "" for node in string_item.findall(".//a:t", _NS))
        strings.append(_normalize_spaces(text))
    return strings


def _read_row_values(
    row_elem: ET.Element,
    shared_strings: list[str],
) -> dict[int, str]:
    values: dict[int, str] = {}
    for cell in row_elem.findall("a:c", _NS):
        cell_ref = cell.attrib.get("r", "")
        column_index = _column_ref_to_index(cell_ref)
        if column_index <= 0:
            continue
        values[column_index] = _read_cell_value(cell, shared_strings)
    return values


def _read_cell_value(cell: ET.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    value_node = cell.find("a:v", _NS)
    if cell_type == "inlineStr":
        inline_text = "".join(node.text or "" for node in cell.findall(".//a:t", _NS))
        return _normalize_spaces(inline_text)

    if value_node is None or value_node.text is None:
        return ""

    raw_value = value_node.text
    if cell_type == "s":
        try:
            return shared_strings[int(raw_value)]
        except (ValueError, IndexError):
            return _normalize_spaces(raw_value)

    return _normalize_spaces(raw_value)


def _column_ref_to_index(cell_ref: str) -> int:
    letters = "".join(ch for ch in cell_ref if ch.isalpha()).upper()
    if not letters:
        return -1

    index = 0
    for ch in letters:
        index = index * 26 + (ord(ch) - ord("A") + 1)
    return index


def _find_column(columns: pd.Index, expected: str) -> str:
    expected_normalized = _normalize_spaces(expected).lower()
    for column in columns:
        if _normalize_spaces(str(column)).lower() == expected_normalized:
            return str(column)
    return expected


def _get_question_columns(columns: pd.Index) -> list[str]:
    result: list[str] = []
    for column in columns:
        column_name = _normalize_spaces(str(column))
        if column_name in _SYSTEM_COLUMNS:
            continue
        if column_name in {
            "Country of the respondent",
            "In what role are you representing your country?",
            "Organization of the respondent",
            "Role in the organization",
            "Which stakeholder groups views are you familiar with?",
            "What is your role/mandate in your country's plans for setting up a National Cancer Data Node (NCDN)?",
        }:
            continue
        result.append(column_name)
    return result


def _normalize_spaces(value: str) -> str:
    # Replace non-breaking spaces and collapse multi-space runs.
    normalized = value.replace("\xa0", " ").replace("\n", " ").replace("\t", " ")
    return re.sub(r"\s{2,}", " ", normalized).strip()


def _normalize_country_key(value: str) -> str:
    text = re.sub(r"[^A-Za-z ]", " ", value).upper()
    return re.sub(r"\s{2,}", " ", text).strip()


def _is_missing(value: str) -> bool:
    normalized = _normalize_spaces(value).lower()
    if normalized in _MISSING_MARKERS:
        return True
    return False


def _normalize_answer_value(
    value: str,
    question_type: str,
    answer_state: str,
) -> str | None:
    if answer_state != "answered":
        return None

    if question_type == "text":
        return mask_text_balanced(value)

    return _normalize_choice_value(value)


def _normalize_choice_value(value: str) -> str:
    normalized = _normalize_spaces(value)
    if ";" in normalized:
        parts = [_normalize_spaces(part) for part in normalized.split(";") if part.strip()]
        return ";".join(parts)
    return normalized


def _infer_question_type(prompt: str, value: str) -> str:
    prompt_lower = prompt.lower()
    normalized = value.lower()

    if "please rank" in prompt_lower or "rank " in prompt_lower:
        return "ranking"
    if "select all that apply" in prompt_lower:
        return "multi_select"
    if ";" in value:
        return "multi_select"

    if normalized in {"yes", "no", "true", "false"}:
        return "boolean"
    if prompt_lower.startswith(("is ", "are ", "do ", "does ", "in your country, is")):
        return "boolean"

    if normalized in {"i don't know", "unknown"}:
        return "single_select"

    if value:
        if len(value) <= 40 and all(ch.isalnum() or ch in " -_/." for ch in value):
            return "single_select"
        return "text"

    return "text"


def _infer_section_id(prompt: str) -> str:
    p = prompt.lower()

    if any(token in p for token in ("metadata", "dataset catalogue", "healthdcat")):
        return "section_metadata"
    if any(token in p for token in ("structural", "data model", "common dataset variables")):
        return "section_structural_standards"
    if any(token in p for token in ("semantic", "ontology", "terminolog", "snomed", "loinc")):
        return "section_semantic_standards"
    if any(token in p for token in ("secure processing environment", "spe", "ehds")):
        return "section_spe_ehds"
    if any(token in p for token in ("ncdn", "governance", "strategy", "operations")):
        return "section_ncdn_operations"
    if any(token in p for token in ("data quality", "quality at source")):
        return "section_data_quality"
    if any(token in p for token in ("infrastructure", "data holders", "collaborate")):
        return "section_data_landscape"
    if any(token in p for token in ("function", "key players", "stakeholder")):
        return "section_functions"
    return "section_general"
