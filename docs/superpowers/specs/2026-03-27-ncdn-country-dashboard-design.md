# NCDN Excel-Backed Dashboard Design

Date: 2026-03-27
Status: Approved for planning

## 1. Objective

Build a country-focused analytics dashboard from the Excel source file:

`data/CANDLE_ Survey for Member States on National Cancer Data Node Plans(1-17).xlsx`

The dashboard must:

- never display respondent name/email
- aggregate by section and question
- show country-level counts and country lists (ISO code only)
- support side-by-side country comparisons
- provide additional insight blocks useful for decision making

## 2. Confirmed Decisions

- Open-text privacy mode: `Balanced`
- Country label style: `ISO code only`
- Data pipeline: `Excel -> normalized Parquet`
- Default landing view: `Section heatmap`
- Small-group suppression: `None` (no minimum-count suppression)
- Country aggregation behavior: show full respondent distribution (no forced majority collapse)

## 3. Architecture

### 3.1 Excel Ingest Layer

- Reads workbook and canonicalizes columns.
- Maps raw survey columns to logical `section_id` and `question_id`.
- Extracts country and converts to standardized ISO code.
- Drops direct identifiers (`Respondent's name`, `Respondent's email`) at ingest.

### 3.2 Privacy + Normalization Layer

- Applies Balanced masking on open-text fields:
  - email-like patterns redacted
  - phone-like patterns redacted
  - person-name-like entities redacted conservatively
- Persists only masked text for analytics.
- Writes normalized Parquet artifacts.

### 3.3 Analytics Layer (DuckDB)

- Provides reusable aggregate queries for:
  - section coverage and answered rates
  - question distributions by country
  - country-vs-country answer deltas
  - divergence, consensus, and missingness insights

### 3.4 Dashboard Layer (Streamlit)

- Uses normalized Parquet as source of truth.
- Provides section-first exploration with country drill-down.
- Exposes comparison and insight pages using aggregate-only outputs.

## 4. Data Model

## 4.1 `respondents`

- `respondent_id` (generated UUID)
- `country_iso`
- non-PII metadata (role, organization, stakeholder groups as available)
- source metadata (`data_source`, ingest timestamp)

## 4.2 `answers`

- `respondent_id`
- `section_id`
- `question_id`
- `question_type`
- `answer_state`
- `answer_value_masked` (for text)

Note: raw free-text is not persisted.

## 4.3 `answer_items` (exploded)

- one row per selected item for multi-select
- one row per rank-item pair for ranking
- supports accurate per-option country comparisons

## 5. Aggregation Rules

- Section country count:
  - distinct `country_iso` with at least one answered question in that section.
- Section country list:
  - sorted unique ISO list for that section.
- Question comparison matrix:
  - rows: answer options
  - columns: countries (`country_iso`)
  - values: count and percentage.
- Heatmap metric (default):
  - `% answered` by `section_id x country_iso`.
- Country-level rollups:
  - retain full within-country respondent distribution.

## 6. Dashboard UX

## 6.1 Overview (Default): Section Heatmap

- Rows: sections
- Columns: ISO countries
- Cell: answer coverage metric
- Interaction: click cell to jump into section-country detail

## 6.2 Section Detail

- Question list for selected section with:
  - countries answered count
  - country ISO list
  - completion indicator
  - compact dominant-answer summary
- Expand per question for full country distribution

## 6.3 Question Comparison

- Side-by-side country comparison:
  - count and percentage pivot
  - chart + table view
- Supports single-select, boolean, multi-select, ranking.
- Text questions use masked thematic summaries and mention counts.

## 6.4 Country Comparison Workspace

- Select N countries + target question/section.
- Show aligned distributions and largest-difference highlights.
- Export aggregate table only (no respondent-level PII).

## 7. Error Handling

- Invalid/missing Excel file: clear failure message with expected path.
- Unmapped country values: flag and route to `UNK` bucket with data-quality warning.
- Unknown question columns: log and list in ingest report.
- Empty filter result sets: show explicit "no data" state, never crash visualizations.

## 8. Testing Strategy

- Unit tests:
  - column-to-question mapping
  - ISO conversion
  - masking functions
  - multi-select/ranking explosion logic
- Integration tests:
  - Excel -> Parquet pipeline on provided workbook
  - DuckDB aggregates match expected totals
- Dashboard smoke tests:
  - each page loads
  - key filters and drill-downs return stable outputs
  - no PII fields rendered in UI tables/charts

## 9. Out of Scope

- Respondent-level identity views
- Raw open-text display
- Statistical weighting or causal inference modules

