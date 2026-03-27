import importlib
import subprocess
import sys
from pathlib import Path

from ms_survey.cli import build_parser


def test_package_imports() -> None:
    module = importlib.import_module("ms_survey")
    assert module is not None


def test_main_help_shows_usage() -> None:
    root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, str(root / "main.py"), "--help"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()


def test_dashboard_has_section_heatmap_page() -> None:
    from ms_survey.dashboard.pages.section_heatmap import render_section_heatmap

    assert render_section_heatmap is not None


def test_cli_has_build_excel_dataset_command() -> None:
    parser = build_parser()
    help_text = parser.format_help()
    assert "build-excel-dataset" in help_text


def test_cli_has_export_static_dashboard_command() -> None:
    parser = build_parser()
    help_text = parser.format_help()
    assert "export-static-dashboard" in help_text
