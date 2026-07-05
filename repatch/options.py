"""File-level option preview patch workflows."""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .spatial import apply_spatial_deletes_to_html

OPTION_PREVIEW_FILES: tuple[tuple[str, str], ...] = (
    ("alt_a.html", "Option A (minimal)"),
    ("alt_b.html", "Option B (balanced)"),
    ("alt_c.html", "Option C (expanded)"),
)

FinalizeHtmlFn = Callable[[str], str]
DeleteResolverFn = Callable[[], list[str]]


def replace_html_title(html: str, title: str) -> str:
    """Replace an existing document title without otherwise changing the document."""
    if re.search(r"<title[^>]*>", html, flags=re.I):
        # Use a replacement function, not an f-string: re.sub interprets
        # backslash sequences (\1, \g<name>, ...) in a string replacement,
        # so a title containing e.g. "\1" would raise re.error (this pattern
        # has no capturing groups) instead of being inserted literally.
        return re.sub(
            r"<title[^>]*>.*?</title>",
            lambda _match: f"<title>{title}</title>",
            str(html or ""),
            count=1,
            flags=re.I | re.S,
        )
    return html


def normalize_html_body(html: str) -> str:
    """Normalize non-behavioral title differences for preview comparison."""
    stripped = re.sub(r"<title[^>]*>.*?</title>", "", str(html or ""), flags=re.I | re.S)
    return stripped.strip()


def html_files_distinct(base_dir: Path | str, names: list[str]) -> bool:
    """True when all named HTML files exist and at least two have different bodies."""
    root = Path(base_dir)
    bodies: list[str] = []
    for name in names:
        path = root / name
        if not path.exists():
            return False
        bodies.append(normalize_html_body(path.read_text(encoding="utf-8")))
    return len(set(bodies)) >= 2


def sync_option_previews_from_workspace(
    cinema_dir: Path | str,
    *,
    stage: int = 0,
    delete_ids: list[str] | None = None,
    delete_resolver: DeleteResolverFn | None = None,
    finalize_html: FinalizeHtmlFn | None = None,
    option_files: tuple[tuple[str, str], ...] = OPTION_PREVIEW_FILES,
) -> dict[str, Any]:
    """
    Refresh Options A-C from the active workspace HTML.

    ``delete_ids=None`` means resolve current policy DELETE ids through
    ``delete_resolver``. ``delete_ids=[]`` mirrors the workspace as-is.
    """
    root = Path(cinema_dir)
    stage_file = root / f"stage{stage}.html"
    if not stage_file.exists():
        return {"error": f"missing {stage_file.name}"}

    html = stage_file.read_text(encoding="utf-8")
    if delete_ids is None and delete_resolver is not None:
        to_delete = list(delete_resolver() or [])
    else:
        to_delete = list(delete_ids or [])

    base, removed = apply_spatial_deletes_to_html(html, to_delete)
    if finalize_html is not None:
        base = finalize_html(base)

    written: list[str] = []
    for filename, title in option_files:
        (root / filename).write_text(replace_html_title(base, title), encoding="utf-8")
        written.append(filename)

    # Mirror options B/C into stage1/stage2, by position in `option_files`
    # rather than a hardcoded "alt_b.html"/"alt_c.html" — a caller passing a
    # custom option_files tuple would otherwise silently read stale/nonexistent
    # default filenames here instead of the files actually just written above.
    if len(option_files) > 1:
        second = root / option_files[1][0]
        if second.exists():
            (root / "stage1.html").write_text(second.read_text(encoding="utf-8"), encoding="utf-8")
    if len(option_files) > 2:
        third = root / option_files[2][0]
        if third.exists():
            (root / "stage2.html").write_text(third.read_text(encoding="utf-8"), encoding="utf-8")

    return {
        "status": "options_synced_from_workspace",
        "stage": stage,
        "files": written,
        "spatial_removed": removed,
        "delete_ids": to_delete,
    }


def enforce_deletes_on_option_previews(
    cinema_dir: Path | str,
    delete_ids: list[str],
    *,
    finalize_html: FinalizeHtmlFn | None = None,
    option_files: tuple[tuple[str, str], ...] = OPTION_PREVIEW_FILES,
) -> dict[str, Any]:
    """Apply DELETE ids to existing Option A-C preview files."""
    effective_delete = [str(x).strip() for x in (delete_ids or []) if str(x).strip()]
    if not effective_delete:
        return {"status": "options_unchanged", "files": [], "delete_ids": []}

    root = Path(cinema_dir)
    touched: list[str] = []
    all_removed: list[str] = []
    for filename, _title in option_files:
        path = root / filename
        if not path.exists():
            continue
        html = path.read_text(encoding="utf-8")
        patched, removed = apply_spatial_deletes_to_html(html, effective_delete)
        if not removed:
            continue
        if finalize_html is not None:
            patched = finalize_html(patched)
        path.write_text(patched, encoding="utf-8")
        touched.append(filename)
        all_removed.extend(removed)

    return {
        "status": "options_patched",
        "files": touched,
        "spatial_removed": sorted(set(all_removed)),
        "delete_ids": effective_delete,
    }
