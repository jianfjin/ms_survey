"""Export normalized dataset to a single-file static HTML dashboard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ms_survey.static_export.html_template import render_dashboard_html
from ms_survey.static_export.payload_builder import (
    build_dashboard_payload,
    serialize_payload,
)


def export_static_dashboard_html(
    dataset_dir: str | Path,
    output_path: str | Path,
    *,
    max_payload_bytes: int = 25 * 1024 * 1024,
    fail_if_pii: bool = True,
) -> dict[str, Any]:
    """Build and write a single self-contained HTML dashboard artifact."""
    payload = build_dashboard_payload(dataset_dir, fail_if_pii=fail_if_pii)
    encoded, serialization_report = serialize_payload(
        payload,
        max_bytes=max_payload_bytes,
    )
    html = render_dashboard_html(
        encoded_payload=encoded,
        export_report=serialization_report,
    )
    output_path = Path(output_path)
    _atomic_write_text(output_path, html)

    return {
        "output_path": str(output_path),
        **serialization_report,
    }


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(path)

