from ms_survey.static_export.html_template import (
    build_client_js,
    build_css_tokens_and_layout,
    render_dashboard_html,
)


def test_render_template_contains_required_regions() -> None:
    html = render_dashboard_html(
        encoded_payload="abc",
        export_report={"size_bytes": 100, "warnings": [], "encoding": "base64+json"},
    )
    assert "<main id=\"app-root\"" in html
    assert "window.__DATA_B64_GZ__" in html
    assert ":root" in html


def test_client_js_contains_required_functions() -> None:
    js = build_client_js()
    assert "function applyFilters(" in js
    assert "function computeSectionHeatmap(" in js
    assert "function computeQuestionDistribution(" in js


def test_template_includes_focus_and_reduced_motion_rules() -> None:
    css = build_css_tokens_and_layout()
    assert ":focus-visible" in css
    assert "@media(prefers-reduced-motion:reduce)" in css

