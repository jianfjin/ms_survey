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

### Privacy behavior

- Respondent name and email are excluded from normalized outputs.
- Open-text answers are masked in Balanced mode (email/phone/person-like names redacted).
- Dashboard visualizations are aggregate-only and country labels are ISO code only.
