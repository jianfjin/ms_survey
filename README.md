## MS Survey Dashboard

### Build normalized dataset from Excel

```bash
uv run ms-survey build-excel-dataset --input "data/CANDLE_ Survey for Member States on National Cancer Data Node Plans(1-17).xlsx" --output-dir data/normalized
```

This command creates:
- `data/normalized/respondents.parquet`
- `data/normalized/questions.parquet`
- `data/normalized/answers.parquet`
- `data/normalized/answer_items.parquet`

### Run dashboard

```bash
uv run streamlit run src/ms_survey/dashboard/app.py
```

### Dashboard analysis guide

After the app starts, use the sidebar in this order:

1. Confirm `Dataset Directory` points to your normalized parquet folder (default: `data/normalized`).
2. Set global filters:
   - `Countries` (default: all countries selected)
   - `Roles` (empty means all roles)
   - `Data Source` (default: all sources selected)
   - `Sections` (empty means all sections)
   - `Question Types` (empty means all types)
3. Use `Navigation` to move through analysis pages.

If the dataset directory does not exist or misses required files, build the dataset first:

```bash
uv run ms-survey build-excel-dataset --input "data/CANDLE_ Survey for Member States on National Cancer Data Node Plans(1-17).xlsx" --output-dir data/normalized
```

Use each page for a specific analysis goal:

1. `Section Heatmap`
   - Start here for overall coverage quality.
   - KPI cards show filtered respondents, country count, and question count.
   - Heatmap shows `% answered` by `section_id x country_iso`.
   - `Most Missing Sections` table highlights lowest-coverage section/country pairs to prioritize follow-up.

2. `Section View`
   - Choose one section and review question-level completion.
   - Main table includes:
     - `countries_answered`: number of countries with at least one answered response
     - `country_iso_list`: countries that answered
     - `answered_count` / `total_count` / `answered_pct`
   - Bar chart (`Countries Answered per Question`) quickly surfaces weakest questions in that section.

3. `Question View`
   - Select one question to inspect distribution and semantics.
   - Structured questions use a Highcharts-inspired dual-axis chart:
     - primary metric: `response_count` (one count per observed answer option response)
     - secondary view: percentage against answered respondents for that question
   - `Answer Summary Table` shows `answer_value`, `response_count`, `respondent_count`, and `%`.
   - For text questions, review:
     - `Masked Theme Cloud` (word-cloud style weighted token view)
     - `Masked Theme Summary` (top token frequencies table)
     - `Masked Text Samples` (privacy-masked excerpts only)

4. `Country Comparison`
   - Select at least two countries and one question for side-by-side comparison.
   - `Percentage Matrix` shows answer distribution per country.
   - `Counts` chart compares absolute respondent counts.
   - `Largest Differences` reports highest percentage-point gaps (`delta_pp`) and which countries are max/min per answer option.

Recommended workflow for reproducible analysis:

1. Find coverage gaps in `Section Heatmap`.
2. Drill into weak sections in `Section View`.
3. Validate answer semantics in `Question View`.
4. Quantify cross-country divergence in `Country Comparison`.
5. Keep filters fixed while moving pages so results stay comparable.

### Export single-file offline HTML dashboard

```bash
uv run ms-survey export-static-dashboard --dataset-dir data/normalized --output dist/dashboard.html
```

This command generates one distributable file:
- `dist/dashboard.html`

End users can open that file directly in a browser without installing Python, running Streamlit, or internet access.

Static `Question Analysis` parity with Streamlit is included in the exported HTML:
- Structured questions use `response_count`-based summaries with Highcharts-inspired dual-axis styling.
- Three alternative biomedical chart modes are available per question: `Horizontal Bar`, `Lollipop`, and `Gradient + Average`.
- Text questions include word-cloud style theme visualization, charted theme distributions, and all masked text responses for active filters.

### Privacy behavior

- Respondent name and email are excluded from normalized outputs.
- Open-text answers are masked in Balanced mode (email/phone/person-like names redacted).
- Streamlit dashboard uses ISO country labels.
