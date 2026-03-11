import importlib
import subprocess
import sys
from pathlib import Path


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
