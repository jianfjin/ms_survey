# Static HTML NCDN Dashboard Design

Date: 2026-03-27
Status: Approved for planning

## 1. Objective

Design a **single, fully offline HTML dashboard** generated from the normalized survey dataset, with full client-side interactivity for biomedical researchers.

The output must be one distributable file:

- `dist/dashboard.html`

No user build step, no backend, no Streamlit runtime required for end users.

## 2. Confirmed Decisions

- Delivery format: single self-contained HTML file
- Runtime: fully offline (no CDN dependencies)
- Interactivity level: full client-side dashboard
- Data scope: include respondent-level normalized rows
- Export mode: one-time explicit export command
- Design target: professional biomedical research dashboard (`ui-ux-pro-max` aligned)

## 3. Architecture

## 3.1 Static Export Engine

Add an exporter that:

1. Reads normalized parquet datasets (`respondents`, `questions`, `answers`, `answer_items`)
2. Builds compact JSON payloads for browser analytics
3. Injects payload + app code + styles into one HTML template
4. Writes `dist/dashboard.html` atomically

## 3.2 Single-File App Shell

The generated HTML contains:

- Embedded CSS design tokens and layout system
- Embedded JS state/store/filter engine
- Embedded charting runtime (offline; no remote scripts)
- Embedded accessibility behavior (keyboard/focus/reduced-motion)

## 3.3 Client-Side Analytics Layer

All analytics are computed in-browser from embedded data:

- section heatmap
- section-level question summaries
- question-level country distributions
- side-by-side multi-country comparison
- delta insights
- masked text theme summaries and samples

## 4. UI/UX System (Biomedical Research)

Visual direction:

- Style: Data-Dense Dashboard
- Tone: clinical, precise, neutral, high legibility

Color system:

- Primary: `#3B82F6`
- Secondary: `#60A5FA`
- Accent: `#F97316`
- Background: `#F8FAFC`
- Text: `#1E293B`

Typography:

- UI/body: Fira Sans
- data labels/compact technical text: Fira Code
- font embedding strategy:
  - preferred: embedded `@font-face` in HTML
  - fallback: system sans/monospace if size threshold exceeded

Layout:

- Left filter rail
- Top KPI strip
- Main analytical canvas with:
  - section heatmap panel
  - question/country comparison panels
  - insight panels

Accessibility requirements:

- text contrast >= 4.5:1
- visible focus rings for all interactive controls
- complete keyboard navigation flow
- `prefers-reduced-motion` support
- chart + table parity (table fallback for every chart)

## 5. Data Flow and Privacy

Input:

- normalized parquet files produced by current pipeline

Export transform:

1. Load normalized tables
2. Derive browser-ready structures for filtering and visualization
3. Embed as serialized payload in `window.__DATA__`
4. Emit export report (record counts, payload size, warnings)

Runtime flow:

1. Initialize store from embedded payload
2. Apply filters (country ISO, role, section, question type)
3. Recompute aggregates client-side
4. Re-render charts and tables synchronously

Privacy invariants:

- no respondent name/email in payload
- open text remains Balanced-masked before embedding
- sensitivity banner in UI indicating respondent-level data is embedded
- optional aggregate-only mode toggle in UI

## 6. Functional Parity Scope

Target parity with current Streamlit analytics features:

- section heatmap
- section/question aggregate summaries
- multi-country side-by-side comparison
- divergence (delta) highlights
- masked text theme/samples

Non-goal:

- Streamlit runtime mechanics (server widgets/session internals) are not replicated.

## 7. Error Handling

Exporter errors:

- missing parquet input
- missing required columns
- privacy invariant violation
- oversized artifact warnings

Browser-side resilience:

- malformed payload -> render diagnostic panel
- chart render failure -> fallback to data table
- empty-filter result -> explicit no-data state

## 8. Testing Strategy

Unit tests:

- payload builder shape and deterministic serialization
- HTML injection integrity
- privacy guard checks
- size threshold warnings

Integration tests:

- normalized parquet -> static HTML export
- open generated HTML and verify core panels render
- country code correctness check (including NL)

UI smoke checks:

- keyboard traversal for all filter and navigation controls
- focus indicator visibility
- contrast sanity checks
- chart/table result parity for selected filters

## 9. Constraints and Trade-offs

Trade-offs accepted:

- larger file size due single-file + offline + respondent-level embed
- client-side compute load for full interactivity

Mitigations:

- optional payload compaction (dictionary encoding / string dedup)
- optional text payload reduction mode for very large exports

## 10. Out of Scope

- backend APIs
- authentication/authorization
- real-time data refresh
- multi-file web deployment bundle

