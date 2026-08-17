#!/usr/bin/env python3
"""Audit a local notebook HTML export before it is retained or shared."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HTML_PATH = REPOSITORY_ROOT / "artifacts" / "html" / "tcc-evolved.html"

FORBIDDEN_PATH_FRAGMENTS = (
    "/content/",
    "/home/",
    "/Users/",
    "C:\\Users\\",
)
FORBIDDEN_CREDENTIAL_FRAGMENTS = (
    "kaggle.json",
    "BEGIN OPENSSH PRIVATE KEY",
    "BEGIN RSA PRIVATE KEY",
)
IDENTIFIER_HEADER_PATTERN = re.compile(
    r"<th\b[^>]*>\s*(?:id|member_id|url|emp_title|desc|title|zip_code)\s*</th>",
    flags=re.IGNORECASE,
)
# This identifier is present in historical Lending Club examples and must never
# reappear in reconstructed notebook outputs or their exported representation.
KNOWN_BORROWER_IDENTIFIER = "1077501"


class LocalHtmlValidationError(RuntimeError):
    """Raised when a local HTML export violates a safety contract."""


def sha256(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def relative_path(path: Path, repository_root: Path = REPOSITORY_ROOT) -> Path:
    """Resolve a path inside the repository or fail clearly."""

    try:
        return path.resolve().relative_to(repository_root.resolve())
    except ValueError as error:
        raise LocalHtmlValidationError(
            "HTML export must remain inside the repository"
        ) from error


def is_ignored(path: Path, repository_root: Path = REPOSITORY_ROOT) -> bool:
    """Return whether Git ignores a path located inside the repository."""

    candidate = relative_path(path, repository_root)
    result = subprocess.run(
        ["git", "check-ignore", "--quiet", "--", candidate.as_posix()],
        cwd=repository_root.resolve(),
        check=False,
    )
    return result.returncode == 0


def validate_html(
    path: Path = DEFAULT_HTML_PATH,
    *,
    repository_root: Path = REPOSITORY_ROOT,
    require_ignored: bool = True,
) -> dict[str, Any]:
    """Validate location and content of one local notebook HTML export."""

    path = path.resolve()
    errors: list[str] = []
    if not path.is_file():
        raise LocalHtmlValidationError(f"HTML export not found: {path}")
    if path.suffix.lower() != ".html":
        errors.append("export must use the .html extension")

    ignored_by_git: bool | None = None
    if require_ignored:
        ignored_by_git = is_ignored(path, repository_root)
        if not ignored_by_git:
            errors.append("HTML export is not ignored by Git")

    html = path.read_text(encoding="utf-8")
    lowered_html = html.lower()
    for fragment in FORBIDDEN_PATH_FRAGMENTS:
        if fragment.lower() in lowered_html:
            errors.append(f"local absolute path found: {fragment}")
    for fragment in FORBIDDEN_CREDENTIAL_FRAGMENTS:
        if fragment.lower() in lowered_html:
            errors.append(f"credential reference found: {fragment}")
    if IDENTIFIER_HEADER_PATTERN.search(html):
        errors.append("table with record-level identifier column found")
    if KNOWN_BORROWER_IDENTIFIER in html:
        errors.append("known borrower identifier found")

    if errors:
        raise LocalHtmlValidationError("\n".join(errors))

    display_path = (
        relative_path(path, repository_root).as_posix()
        if require_ignored
        else path.as_posix()
    )
    return {
        "path": display_path,
        "size_bytes": path.stat().st_size,
        "sha256": sha256(path),
        "ignored_by_git": ignored_by_git,
        "absolute_paths_found": 0,
        "record_identifier_tables_found": 0,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "html_path",
        nargs="?",
        type=Path,
        default=DEFAULT_HTML_PATH,
        help="local HTML export to audit",
    )
    return parser.parse_args()


def print_json_summary(summary: dict[str, Any]) -> int:
    """Print one deterministic command-line summary and return success."""

    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def main() -> int:
    args = parse_args()
    try:
        summary = validate_html(args.html_path)
    except (LocalHtmlValidationError, OSError, UnicodeError) as error:
        print(f"ERROR  {error}")
        return 1
    return print_json_summary(summary)


if __name__ == "__main__":
    raise SystemExit(main())
