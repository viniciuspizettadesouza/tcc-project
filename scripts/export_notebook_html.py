#!/usr/bin/env python3
"""Export one saved project notebook to a complete, audited local HTML."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import nbformat
import plotly.graph_objects as go
import plotly.io as pio
from nbconvert import HTMLExporter

try:
    from scripts.validate_local_html import (
        DEFAULT_HTML_PATH,
        LocalHtmlValidationError,
        print_json_summary,
        validate_html,
    )
except ModuleNotFoundError:  # Support direct execution from the scripts directory.
    from validate_local_html import (  # type: ignore[no-redef]
        DEFAULT_HTML_PATH,
        LocalHtmlValidationError,
        print_json_summary,
        validate_html,
    )

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NOTEBOOK_PATH = REPOSITORY_ROOT / "notebooks" / "tcc-evolved.ipynb"
PLOTLY_MIME_TYPE = "application/vnd.plotly.v1+json"


def add_plotly_html(notebook: Any) -> int:
    """Add an offline HTML representation beside each saved Plotly MIME output."""

    converted = 0
    for cell in notebook.cells:
        for output in cell.get("outputs", []):
            data = output.get("data", {})
            payload = data.get(PLOTLY_MIME_TYPE)
            if payload is None or "text/html" in data:
                continue
            figure = go.Figure(
                data=payload.get("data", []), layout=payload.get("layout")
            )
            data["text/html"] = pio.to_html(
                figure,
                config=payload.get("config"),
                full_html=False,
                include_plotlyjs=True,
            )
            converted += 1
    return converted


def export_notebook(
    notebook_path: Path = DEFAULT_NOTEBOOK_PATH,
    html_path: Path = DEFAULT_HTML_PATH,
) -> dict[str, Any]:
    """Export one saved notebook and audit the resulting ignored HTML."""

    notebook = nbformat.read(notebook_path, as_version=4)
    nbformat.validate(notebook)
    converted_plotly_outputs = add_plotly_html(notebook)
    exporter = HTMLExporter()
    body, _ = exporter.from_notebook_node(notebook)

    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(body, encoding="utf-8")
    summary = validate_html(html_path)
    summary["plotly_outputs_embedded"] = converted_plotly_outputs
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--notebook",
        type=Path,
        default=DEFAULT_NOTEBOOK_PATH,
        help="saved notebook to export",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_HTML_PATH,
        help="ignored local HTML destination",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        summary = export_notebook(args.notebook.resolve(), args.output.resolve())
    except (LocalHtmlValidationError, OSError, UnicodeError, ValueError) as error:
        print(f"ERROR  {error}")
        return 1
    return print_json_summary(summary)


if __name__ == "__main__":
    raise SystemExit(main())
